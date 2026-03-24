#!/usr/bin/env python3
"""
Cross‑method validation: compare lattice, PDE, and Monte Carlo (LSM) for call/put spreads.
Visualise option values and exercise premiums across a spot grid.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import monte_carlo
import pde
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.interpolate import interp1d
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

# ---------- Extended Monte Carlo with option_type ----------
def lsm_value_with_type(
    n_paths: int,
    n_steps: int,
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma_spot: float,
    sigma_fair_func,
    sigma_offset: float,
    option_type: str = 'call',
    basis_funcs = None,
):
    """
    LSM valuation for call or put spreads.
    """
    if option_type not in ('call', 'put'):
        raise ValueError("option_type must be 'call' or 'put'")
    
    # Choose Black‑Scholes pricing function
    if option_type == 'call':
        price_func = lattice.black_scholes_call
    else:
        price_func = lattice.black_scholes_put
    
    if basis_funcs is None:
        basis_funcs = [lambda x: np.ones_like(x), lambda x: x, lambda x: x ** 2]
    
    dt = T / (n_steps - 1) if n_steps > 1 else T
    # Simulate GBM paths (antithetic)
    np.random.seed(12345)
    Z = np.random.randn(n_paths // 2, n_steps - 1)
    Z = np.vstack([Z, -Z])
    if Z.shape[0] < n_paths:
        extra = np.random.randn(n_paths - Z.shape[0], n_steps - 1)
        Z = np.vstack([Z, extra])
    
    S = np.zeros((n_paths, n_steps))
    S[:, 0] = S0
    for t in range(1, n_steps):
        S[:, t] = S[:, t - 1] * np.exp(
            (r - 0.5 * sigma_spot ** 2) * dt + sigma_spot * np.sqrt(dt) * Z[:, t - 1])
    
    # Immediate exercise value
    exercise_value = np.zeros_like(S)
    for t in range(n_steps):
        time_to_expiry = T - t * dt
        for p in range(n_paths):
            spot = S[p, t]
            vol_low = sigma_fair_func(spot)
            vol_high = vol_low + sigma_offset
            price_low = price_func(spot, K, time_to_expiry, r, vol_low)
            price_high = price_func(spot, K, time_to_expiry, r, vol_high)
            exercise_value[p, t] = price_high - price_low
    
    cashflow = np.zeros_like(S)
    cashflow[:, -1] = exercise_value[:, -1]
    
    # Backward induction
    for t in range(n_steps - 2, -1, -1):
        itm = exercise_value[:, t] > 0
        if np.sum(itm) == 0:
            cashflow[:, t] = cashflow[:, t + 1] * np.exp(-r * dt)
            continue
        X = np.column_stack([func(S[itm, t]) for func in basis_funcs])
        Y = cashflow[itm, t + 1] * np.exp(-r * dt)
        beta = np.linalg.lstsq(X, Y, rcond=None)[0]
        continuation_estimate = X @ beta
        exercise = exercise_value[itm, t] >= continuation_estimate
        cashflow[itm, t] = np.where(exercise,
                                     exercise_value[itm, t],
                                     cashflow[itm, t + 1] * np.exp(-r * dt))
        cashflow[~itm, t] = cashflow[~itm, t + 1] * np.exp(-r * dt)
    
    value = np.mean(cashflow[:, 0])
    # Exercise boundary: minimum spot where exercise occurred
    boundary = np.full(n_steps, np.inf)
    for t in range(n_steps):
        exercised = cashflow[:, t] == exercise_value[:, t]
        if np.any(exercised):
            boundary[t] = np.min(S[exercised, t])
    
    return value, boundary

# ---------- Extended PDE with option_type ----------
def pde_value_with_type(
    S_min: float,
    S_max: float,
    n_S: int,
    n_t: int,
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma_spot: float,
    sigma_fair_func,
    sigma_offset: float,
    option_type: str = 'call',
    method: str = 'implicit',
    omega: float = 1.2,
    max_iter: int = 100,
    tol: float = 1e-8,
):
    """
    PDE valuation for call or put spreads.
    """
    if option_type not in ('call', 'put'):
        raise ValueError("option_type must be 'call' or 'put'")
    
    if option_type == 'call':
        price_func = lattice.black_scholes_call
    else:
        price_func = lattice.black_scholes_put
    
    S_grid = np.linspace(S_min, S_max, n_S)
    dS = S_grid[1] - S_grid[0]
    dt = T / n_t
    
    # Unwind values on grid
    unwind = np.zeros((n_S, n_t + 1))
    for i, S in enumerate(S_grid):
        for j in range(n_t + 1):
            t = j * dt
            time_to_expiry = T - t
            vol_low = sigma_fair_func(S)
            vol_high = vol_low + sigma_offset
            price_low = price_func(S, K, time_to_expiry, r, vol_low)
            price_high = price_func(S, K, time_to_expiry, r, vol_high)
            unwind[i, j] = price_high - price_low
    
    # Initialise value at maturity
    V = unwind[:, -1].copy()
    V_history = np.zeros((n_S, n_t + 1))
    V_history[:, -1] = V
    
    # Finite‑difference coefficients
    alpha = np.zeros(n_S)
    beta = np.zeros(n_S)
    gamma = np.zeros(n_S)
    for i in range(1, n_S - 1):
        S = S_grid[i]
        alpha[i] = 0.5 * sigma_spot ** 2 * S ** 2 / (dS ** 2) - r * S / (2 * dS)
        beta[i] = -sigma_spot ** 2 * S ** 2 / (dS ** 2) - r
        gamma[i] = 0.5 * sigma_spot ** 2 * S ** 2 / (dS ** 2) + r * S / (2 * dS)
    
    alpha[0] = 0.0
    beta[0] = 1.0
    gamma[0] = 0.0
    alpha[-1] = 0.0
    beta[-1] = 1.0
    gamma[-1] = 0.0
    
    diag = 1 - dt * beta
    sub = -dt * alpha[1:]
    sup = -dt * gamma[:-1]
    
    # Time stepping backward
    exercise_boundary = np.full(n_t + 1, np.inf)
    meaningful = unwind[:, -1] > 1e-3
    if np.any(meaningful):
        exercise_boundary[-1] = np.min(S_grid[meaningful])
    
    for step in range(n_t - 1, -1, -1):
        V_old = V.copy()
        phi = unwind[:, step]
        
        V_new = V_old.copy()
        for it in range(max_iter):
            V_prev = V_new.copy()
            for i in range(n_S):
                sigma = 0.0
                if i > 0:
                    sigma += sub[i-1] * V_new[i-1]
                if i < n_S - 1:
                    sigma += sup[i] * V_prev[i+1]
                v = (V_old[i] - sigma) / diag[i]
                v = max(v, phi[i])
                V_new[i] = V_prev[i] + omega * (v - V_prev[i])
            if np.max(np.abs(V_new - V_prev)) < tol:
                break
        
        V = V_new
        V_history[:, step] = V
        
        meaningful = phi > 1e-3
        binding = np.abs(V - phi) < 1e-6
        exercise = meaningful & binding
        if np.any(exercise):
            exercise_boundary[step] = np.min(S_grid[exercise])
    
    # Interpolate to S0
    value = np.interp(S0, S_grid, V)
    # Create interpolation function for other spots
    interp_func = interp1d(S_grid, V, kind='linear', bounds_error=False, fill_value='extrapolate')
    
    return value, interp_func, exercise_boundary, S_grid, V

# ---------- Main validation ----------
def main():
    # Fixed parameters
    sigma_fair = 0.2
    K = 100.0
    S0 = 100.0
    T = 1.0
    r = 0.05
    
    # Parameter ranges
    sigma_offset_list = [0.0, 0.05]
    sigma_spot_list = [0.1, 0.5]   # from <sigma_fair to >2*(sigma_fair+max_offset)
    option_types = ['call', 'put']
    
    # Spot grid for valuation curves
    spot_grid = np.linspace(50, 150, 11)   # 11 points from 50 to 150
    
    # Numerical settings
    lattice_n = 50
    mc_n_paths = 2000
    mc_n_steps = 30
    pde_S_min = 1.0
    pde_S_max = 300.0
    pde_n_S = 80
    pde_n_t = 30
    
    sigma_fair_func = lambda s: sigma_fair
    
    # Storage for results
    rows = []
    # For plotting: collect data per (sigma_spot, sigma_offset, option_type)
    plot_data = []
    
    total_combos = len(sigma_spot_list) * len(sigma_offset_list) * len(option_types)
    combo_idx = 0
    
    for sigma_spot in sigma_spot_list:
        for sigma_offset in sigma_offset_list:
            for option_type in option_types:
                combo_idx += 1
                print(f'[{combo_idx}/{total_combos}] σ_spot={sigma_spot:.2f}, σ_offset={sigma_offset:.2f}, {option_type}')
                
                # 1) Lattice values across spot grid
                lattice_vals = []
                for spot in spot_grid:
                    amer, _, _ = lattice.binomial_tree_value(
                        lattice_n, spot, K, T, r, sigma_spot, sigma_fair_func,
                        sigma_offset, option_type=option_type)
                    lattice_vals.append(amer)
                lattice_vals = np.array(lattice_vals)
                
                # 2) PDE values across spot grid (run once, interpolate)
                pde_val_at_S0, pde_interp, pde_boundary, pde_S_grid, pde_V = pde_value_with_type(
                    pde_S_min, pde_S_max, pde_n_S, pde_n_t, S0, K, T, r, sigma_spot,
                    sigma_fair_func, sigma_offset, option_type=option_type)
                pde_vals = pde_interp(spot_grid)
                
                # 3) Monte Carlo value at S0 only
                mc_val, mc_boundary = lsm_value_with_type(
                    mc_n_paths, mc_n_steps, S0, K, T, r, sigma_spot,
                    sigma_fair_func, sigma_offset, option_type=option_type)
                
                # 4) European spread value (for early‑exercise premium)
                if option_type == 'call':
                    euro = lattice.black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - \
                           lattice.black_scholes_call(S0, K, T, r, sigma_fair)
                else:
                    euro = lattice.black_scholes_put(S0, K, T, r, sigma_fair + sigma_offset) - \
                           lattice.black_scholes_put(S0, K, T, r, sigma_fair)
                early_premium_lattice = lattice_vals[spot_grid == S0][0] - euro
                early_premium_pde = pde_val_at_S0 - euro
                early_premium_mc = mc_val - euro
                
                # 5) Exercise premium across spot grid (lattice only)
                premium = []
                boundaries = []  # zero‑crossings
                for spot in spot_grid:
                    # Unwind value
                    if option_type == 'call':
                        unwind = lattice.black_scholes_call(spot, K, T, r, sigma_fair + sigma_offset) - \
                                 lattice.black_scholes_call(spot, K, T, r, sigma_fair)
                    else:
                        unwind = lattice.black_scholes_put(spot, K, T, r, sigma_fair + sigma_offset) - \
                                 lattice.black_scholes_put(spot, K, T, r, sigma_fair)
                    # Continuation value via small lattice
                    n_small = 5
                    dt_small = T / n_small
                    u_small = np.exp(sigma_spot * np.sqrt(dt_small))
                    d_small = 1 / u_small
                    q_small = (np.exp(r * dt_small) - d_small) / (u_small - d_small)
                    val_up, _, _ = lattice.binomial_tree_value(
                        n_small - 1, spot * u_small, K, T - dt_small, r, sigma_spot,
                        sigma_fair_func, sigma_offset, option_type=option_type)
                    val_down, _, _ = lattice.binomial_tree_value(
                        n_small - 1, spot * d_small, K, T - dt_small, r, sigma_spot,
                        sigma_fair_func, sigma_offset, option_type=option_type)
                    cont = np.exp(-r * dt_small) * (q_small * val_up + (1 - q_small) * val_down)
                    premium.append(unwind - cont)
                premium = np.array(premium)
                
                # Find zero‑crossings (boundaries)
                zero_cross = []
                for k in range(len(spot_grid) - 1):
                    if premium[k] * premium[k+1] <= 0:
                        x0, x1 = spot_grid[k], spot_grid[k+1]
                        y0, y1 = premium[k], premium[k+1]
                        if abs(y1 - y0) < 1e-12:
                            zero = (x0 + x1) / 2
                        else:
                            zero = x0 - y0 * (x1 - x0) / (y1 - y0)
                        zero_cross.append(zero)
                # Determine lower/upper boundaries
                if len(zero_cross) == 0:
                    if all(p >= 0 for p in premium):
                        lower = -np.inf
                        upper = np.inf
                    else:
                        lower = np.nan
                        upper = np.nan
                elif len(zero_cross) == 1:
                    z = zero_cross[0]
                    idx = np.where(spot_grid > z)[0][0]
                    if premium[idx] >= 0:
                        lower = z
                        upper = np.inf
                    else:
                        lower = -np.inf
                        upper = z
                else:
                    zero_cross.sort()
                    lower = zero_cross[0]
                    upper = zero_cross[-1]
                
                # Store row for CSV
                rows.append({
                    'sigma_spot': sigma_spot,
                    'sigma_offset': sigma_offset,
                    'option_type': option_type,
                    'lattice_value_S0': lattice_vals[spot_grid == S0][0],
                    'pde_value_S0': pde_val_at_S0,
                    'mc_value_S0': mc_val,
                    'european_value_S0': euro,
                    'early_exercise_premium_lattice': early_premium_lattice,
                    'early_exercise_premium_pde': early_premium_pde,
                    'early_exercise_premium_mc': early_premium_mc,
                    'lower_boundary': lower,
                    'upper_boundary': upper,
                    'num_zero_crossings': len(zero_cross),
                })
                
                # Store for plotting
                plot_data.append({
                    'sigma_spot': sigma_spot,
                    'sigma_offset': sigma_offset,
                    'option_type': option_type,
                    'spot_grid': spot_grid.copy(),
                    'lattice_vals': lattice_vals.copy(),
                    'pde_vals': pde_vals.copy(),
                    'mc_val_S0': mc_val,
                    'premium': premium.copy(),
                    'zero_crossings': zero_cross,
                    'lower_boundary': lower,
                    'upper_boundary': upper,
                })
    
    # ---------- Save CSV ----------
    df = pd.DataFrame(rows)
    csv_path = 'output/cross_method_summary.csv'
    df.to_csv(csv_path, index=False)
    print(f'\n✅ Summary CSV saved to {csv_path}')
    
    # ---------- Plot 1: Option values ----------
    # Layout: rows = sigma_spot, columns = call (left) / put (right)
    fig1, axes1 = plt.subplots(len(sigma_spot_list), 2, figsize=(12, 3 * len(sigma_spot_list)))
    fig1.suptitle('Option value vs spot – lattice (solid), PDE (×), MC (+) | σ_fair=0.2', fontsize=16)
    
    # Color mapping for sigma_offset
    offset_colors = {off: cm.viridis(i / (len(sigma_offset_list) - 1))
                     for i, off in enumerate(sigma_offset_list)}
    
    for row, sigma_spot in enumerate(sigma_spot_list):
        ax_call = axes1[row, 0]
        ax_put = axes1[row, 1]
        for sigma_offset in sigma_offset_list:
            color = offset_colors[sigma_offset]
            # Call spread
            call_data = [d for d in plot_data if
                         d['sigma_spot'] == sigma_spot and
                         d['sigma_offset'] == sigma_offset and
                         d['option_type'] == 'call'][0]
            ax_call.plot(call_data['spot_grid'], call_data['lattice_vals'],
                         color=color, linewidth=2, label=f'σ_offset={sigma_offset:.2f}' if row == 0 else None)
            ax_call.scatter(call_data['spot_grid'], call_data['pde_vals'],
                           marker='x', s=30, color=color, alpha=0.7)
            ax_call.scatter(S0, call_data['mc_val_S0'],
                           marker='+', s=80, color=color, linewidths=2)
            # Put spread
            put_data = [d for d in plot_data if
                        d['sigma_spot'] == sigma_spot and
                        d['sigma_offset'] == sigma_offset and
                        d['option_type'] == 'put'][0]
            ax_put.plot(put_data['spot_grid'], put_data['lattice_vals'],
                        color=color, linewidth=2, label=f'σ_offset={sigma_offset:.2f}' if row == 0 else None)
            ax_put.scatter(put_data['spot_grid'], put_data['pde_vals'],
                          marker='x', s=30, color=color, alpha=0.7)
            ax_put.scatter(S0, put_data['mc_val_S0'],
                          marker='+', s=80, color=color, linewidths=2)
        
        ax_call.axvline(K, color='g', linestyle=':', linewidth=1, label='K')
        ax_call.set_xlabel('Spot')
        ax_call.set_ylabel('Option value')
        ax_call.set_title(f'Call spread, σ_spot={sigma_spot:.2f}')
        ax_call.grid(True, alpha=0.3)
        if row == 0:
            ax_call.legend(loc='upper left', fontsize='small')
        
        ax_put.axvline(K, color='g', linestyle=':', linewidth=1, label='K')
        ax_put.set_xlabel('Spot')
        ax_put.set_ylabel('Option value')
        ax_put.set_title(f'Put spread, σ_spot={sigma_spot:.2f}')
        ax_put.grid(True, alpha=0.3)
        if row == 0:
            ax_put.legend(loc='upper left', fontsize='small')
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig('output/cross_method_option_values.png', dpi=150)
    plt.close()
    
    # ---------- Plot 2: Exercise premium with boundaries ----------
    fig2, axes2 = plt.subplots(len(sigma_spot_list), 2, figsize=(12, 3 * len(sigma_spot_list)))
    fig2.suptitle('Exercise premium (unwind – continuation) with boundaries | σ_fair=0.2', fontsize=16)
    
    for row, sigma_spot in enumerate(sigma_spot_list):
        ax_call = axes2[row, 0]
        ax_put = axes2[row, 1]
        for sigma_offset in sigma_offset_list:
            color = offset_colors[sigma_offset]
            # Call spread
            call_data = [d for d in plot_data if
                         d['sigma_spot'] == sigma_spot and
                         d['sigma_offset'] == sigma_offset and
                         d['option_type'] == 'call'][0]
            ax_call.plot(call_data['spot_grid'], call_data['premium'],
                         color=color, linewidth=2, label=f'σ_offset={sigma_offset:.2f}' if row == 0 else None)
            # Draw vertical dash lines at boundaries
            if not np.isnan(call_data['lower_boundary']) and not np.isinf(call_data['lower_boundary']):
                ax_call.axvline(call_data['lower_boundary'], color=color, linestyle='--', linewidth=1)
            if not np.isnan(call_data['upper_boundary']) and not np.isinf(call_data['upper_boundary']):
                ax_call.axvline(call_data['upper_boundary'], color=color, linestyle='--', linewidth=1)
            # Put spread
            put_data = [d for d in plot_data if
                        d['sigma_spot'] == sigma_spot and
                        d['sigma_offset'] == sigma_offset and
                        d['option_type'] == 'put'][0]
            ax_put.plot(put_data['spot_grid'], put_data['premium'],
                        color=color, linewidth=2, label=f'σ_offset={sigma_offset:.2f}' if row == 0 else None)
            if not np.isnan(put_data['lower_boundary']) and not np.isinf(put_data['lower_boundary']):
                ax_put.axvline(put_data['lower_boundary'], color=color, linestyle='--', linewidth=1)
            if not np.isnan(put_data['upper_boundary']) and not np.isinf(put_data['upper_boundary']):
                ax_put.axvline(put_data['upper_boundary'], color=color, linestyle='--', linewidth=1)
        
        ax_call.axhline(0, color='k', linestyle='--', linewidth=0.8)
        ax_call.axvline(K, color='g', linestyle=':', linewidth=1, label='K')
        ax_call.set_xlabel('Spot')
        ax_call.set_ylabel('Premium')
        ax_call.set_title(f'Call spread, σ_spot={sigma_spot:.2f}')
        ax_call.grid(True, alpha=0.3)
        if row == 0:
            ax_call.legend(loc='upper left', fontsize='small')
        
        ax_put.axhline(0, color='k', linestyle='--', linewidth=0.8)
        ax_put.axvline(K, color='g', linestyle=':', linewidth=1, label='K')
        ax_put.set_xlabel('Spot')
        ax_put.set_ylabel('Premium')
        ax_put.set_title(f'Put spread, σ_spot={sigma_spot:.2f}')
        ax_put.grid(True, alpha=0.3)
        if row == 0:
            ax_put.legend(loc='upper left', fontsize='small')
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig('output/cross_method_premium_boundaries.png', dpi=150)
    plt.close()
    
    print('✅ Generated plots:')
    print('   - cross_method_option_values.png')
    print('   - cross_method_premium_boundaries.png')
    
    # ---------- Statistical summary ----------
    print('\n=== Statistical comparison (values at S₀) ===')
    diff_lattice_pde = df['lattice_value_S0'] - df['pde_value_S0']
    diff_lattice_mc = df['lattice_value_S0'] - df['mc_value_S0']
    diff_pde_mc = df['pde_value_S0'] - df['mc_value_S0']
    print(f'Lattice – PDE: mean={diff_lattice_pde.mean():.6f}, std={diff_lattice_pde.std():.6f}, max={diff_lattice_pde.max():.6f}')
    print(f'Lattice – MC:  mean={diff_lattice_mc.mean():.6f}, std={diff_lattice_mc.std():.6f}, max={diff_lattice_mc.max():.6f}')
    print(f'PDE – MC:      mean={diff_pde_mc.mean():.6f}, std={diff_pde_mc.std():.6f}, max={diff_pde_mc.max():.6f}')
    
    # Summary of boundaries
    finite = df[~np.isinf(df['lower_boundary']) & ~np.isinf(df['upper_boundary'])]
    print(f'\nFinite exercise intervals (both boundaries finite): {len(finite)} combos')
    if len(finite) > 0:
        print(f'  Lower boundary range: [{finite["lower_boundary"].min():.1f}, {finite["lower_boundary"].max():.1f}]')
        print(f'  Upper boundary range: [{finite["upper_boundary"].min():.1f}, {finite["upper_boundary"].max():.1f}]')
    
    # Count combos with zero premium
    zero_premium = df[df['early_exercise_premium_lattice'].abs() < 1e-6]
    print(f'\nZero early‑exercise premium (lattice): {len(zero_premium)} combos')
    
    return df

if __name__ == '__main__':
    main()