#!/usr/bin/env python3
"""
Compare exercise boundaries (lower & upper) across lattice, PDE, and Monte Carlo
using fine spot grid and internal exercise‑region detection.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import monte_carlo
import pde
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

# ---------- Lattice premium with small‑tree continuation ----------
def lattice_premium_fine(
    spots: np.ndarray,
    K: float,
    T: float,
    r: float,
    sigma_spot: float,
    sigma_fair_func,
    sigma_offset: float,
    option_type: str = 'call',
    n_small: int = 5,
) -> np.ndarray:
    """
    Premium = unwind(S) - continuation(S) where continuation is computed via a
    small binomial tree with n_small steps starting from spot S.
    """
    premium = np.zeros_like(spots)
    dt = T / n_small
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    q = (np.exp(r * dt) - d) / (u - d)
    
    for idx, spot in enumerate(spots):
        # Unwind (European spread)
        if option_type == 'call':
            unwind = lattice.black_scholes_call(spot, K, T, r, sigma_fair_func(spot) + sigma_offset) - \
                     lattice.black_scholes_call(spot, K, T, r, sigma_fair_func(spot))
        else:
            unwind = lattice.black_scholes_put(spot, K, T, r, sigma_fair_func(spot) + sigma_offset) - \
                     lattice.black_scholes_put(spot, K, T, r, sigma_fair_func(spot))
        
        # Continuation via small tree
        S_up = spot * u
        S_down = spot * d
        # American spread values at up/down states (full lattice)
        val_up, _, _ = lattice.binomial_tree_value(
            n_small - 1, S_up, K, T - dt, r, sigma_spot, sigma_fair_func,
            sigma_offset, option_type=option_type)
        val_down, _, _ = lattice.binomial_tree_value(
            n_small - 1, S_down, K, T - dt, r, sigma_spot, sigma_fair_func,
            sigma_offset, option_type=option_type)
        continuation = np.exp(-r * dt) * (q * val_up + (1 - q) * val_down)
        premium[idx] = unwind - continuation
    return premium

# ---------- PDE with min/max exercise detection ----------
def pde_value_with_min_max(
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
    PDE valuation returning (value, interp_func, exercise_min, exercise_max, S_grid, V).
    exercise_min/max are the smallest/largest spot where exercise occurs at t=0.
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
    
    # Coefficients
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
    exercise_min = np.full(n_t + 1, np.inf)
    exercise_max = np.full(n_t + 1, -np.inf)
    # At maturity
    meaningful = unwind[:, -1] > 1e-3
    if np.any(meaningful):
        exercise_min[-1] = np.min(S_grid[meaningful])
        exercise_max[-1] = np.max(S_grid[meaningful])
    
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
        
        # Detect exercise region at this time step
        meaningful = phi > 1e-3
        binding = np.abs(V - phi) < 1e-6
        exercise = meaningful & binding
        if np.any(exercise):
            exercise_min[step] = np.min(S_grid[exercise])
            exercise_max[step] = np.max(S_grid[exercise])
    
    value = np.interp(S0, S_grid, V)
    from scipy.interpolate import interp1d
    interp_func = interp1d(S_grid, V, kind='linear', bounds_error=False, fill_value='extrapolate')
    
    return value, interp_func, exercise_min, exercise_max, S_grid, V

# ---------- Monte Carlo with min/max exercise detection ----------
def lsm_value_with_min_max(
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
    LSM valuation returning (value, exercise_min, exercise_max).
    exercise_min/max are the smallest/largest spot where exercise occurs at t=0.
    """
    if option_type not in ('call', 'put'):
        raise ValueError("option_type must be 'call' or 'put'")
    
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
    
    # Exercise region at t=0
    exercised = cashflow[:, 0] == exercise_value[:, 0]
    if np.any(exercised):
        exercise_min = np.min(S[exercised, 0])
        exercise_max = np.max(S[exercised, 0])
    else:
        exercise_min = np.inf
        exercise_max = -np.inf
    
    return value, exercise_min, exercise_max

# ---------- Main ----------
def main():
    # Focus on the finite‑interval case
    sigma_fair = 0.2
    sigma_offset = 0.05
    sigma_spot = 0.5
    K = 100.0
    S0 = 100.0
    T = 1.0
    r = 0.05
    option_types = ['call', 'put']
    
    # Fine spot grid for lattice premium
    spots_fine = np.linspace(50, 150, 101)
    sigma_fair_func = lambda s: sigma_fair
    
    # Numerical settings
    lattice_n = 50
    pde_S_min = 1.0
    pde_S_max = 300.0
    pde_n_S = 80
    pde_n_t = 30
    mc_n_paths = 500   # increased for better detection
    mc_n_steps = 20
    
    rows = []
    
    for option_type in option_types:
        print(f'Processing {option_type} spread...')
        
        # 1. Lattice premium (fine)
        premium_lat = lattice_premium_fine(
            spots_fine, K, T, r, sigma_spot, sigma_fair_func,
            sigma_offset, option_type=option_type, n_small=5)
        
        # Find zero‑crossings
        zero_cross = []
        for k in range(len(spots_fine) - 1):
            y0, y1 = premium_lat[k], premium_lat[k+1]
            if y0 * y1 <= 0:
                x0, x1 = spots_fine[k], spots_fine[k+1]
                if abs(y1 - y0) < 1e-12:
                    zero = (x0 + x1) / 2
                else:
                    zero = x0 - y0 * (x1 - x0) / (y1 - y0)
                zero_cross.append(zero)
        
        if zero_cross:
            lower_lat = zero_cross[0]
            upper_lat = zero_cross[-1]
        else:
            # Determine if premium always positive or negative
            if all(p >= -1e-9 for p in premium_lat):
                lower_lat = -np.inf
                upper_lat = np.inf
            elif all(p <= 1e-9 for p in premium_lat):
                lower_lat = np.inf
                upper_lat = -np.inf
            else:
                lower_lat = np.nan
                upper_lat = np.nan
        
        # 2. PDE internal exercise region at t=0
        _, _, pde_min, pde_max, _, _ = pde_value_with_min_max(
            pde_S_min, pde_S_max, pde_n_S, pde_n_t, S0, K, T, r, sigma_spot,
            sigma_fair_func, sigma_offset, option_type=option_type)
        pde_lower = pde_min[0] if not np.isinf(pde_min[0]) else np.nan
        pde_upper = pde_max[0] if not np.isinf(pde_max[0]) else np.nan
        
        # 3. Monte Carlo internal exercise region at t=0
        _, mc_lower, mc_upper = lsm_value_with_min_max(
            mc_n_paths, mc_n_steps, S0, K, T, r, sigma_spot,
            sigma_fair_func, sigma_offset, option_type=option_type)
        mc_lower = mc_lower if not np.isinf(mc_lower) else np.nan
        mc_upper = mc_upper if not np.isinf(mc_upper) else np.nan
        
        rows.append({
            'option_type': option_type,
            'lower_lattice': lower_lat,
            'upper_lattice': upper_lat,
            'num_zero_crossings_lattice': len(zero_cross),
            'lower_pde_internal': pde_lower,
            'upper_pde_internal': pde_upper,
            'lower_mc_internal': mc_lower,
            'upper_mc_internal': mc_upper,
        })
        
        # Print premium curve shape
        pos = np.sum(premium_lat > 1e-6)
        neg = np.sum(premium_lat < -1e-6)
        zero = np.sum(np.abs(premium_lat) <= 1e-6)
        print(f'  Premium >0: {pos}, <0: {neg}, ≈0: {zero}')
        print(f'  Zero‑crossings: {zero_cross}')
    
    df = pd.DataFrame(rows)
    out_path = 'output/boundary_fine_comparison.csv'
    df.to_csv(out_path, index=False)
    print(f'\n✅ Detailed boundary comparison saved to {out_path}')
    
    # Display summary
    print('\n=== Boundary Comparison (σ_spot=0.5, σ_offset=0.05) ===')
    for _, row in df.iterrows():
        print(f"\n{row['option_type'].upper()} spread:")
        print(f"  Lattice (premium zero‑crossing): [{row['lower_lattice']:.2f}, {row['upper_lattice']:.2f}]")
        print(f"  PDE internal (min/max exercise): [{row['lower_pde_internal']:.2f}, {row['upper_pde_internal']:.2f}]")
        print(f"  MC internal (min/max exercise):  [{row['lower_mc_internal']:.2f}, {row['upper_mc_internal']:.2f}]")
    
    # Plot premium curves for lattice
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (idx, row) in zip(axes, df.iterrows()):
        opt = row['option_type']
        premium = lattice_premium_fine(
            spots_fine, K, T, r, sigma_spot, sigma_fair_func,
            sigma_offset, option_type=opt, n_small=5)
        ax.plot(spots_fine, premium, 'b-', linewidth=2, label='Premium')
        ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
        ax.axvline(K, color='g', linestyle=':', label='K')
        if not np.isnan(row['lower_lattice']) and not np.isinf(row['lower_lattice']):
            ax.axvline(row['lower_lattice'], color='r', linestyle='--', label='Lower bound')
        if not np.isnan(row['upper_lattice']) and not np.isinf(row['upper_lattice']):
            ax.axvline(row['upper_lattice'], color='r', linestyle='--', label='Upper bound')
        ax.set_xlabel('Spot')
        ax.set_ylabel('Premium (unwind – continuation)')
        ax.set_title(f'{opt.capitalize()} spread premium (lattice)')
        ax.grid(True, alpha=0.3)
        ax.legend()
    plt.tight_layout()
    plt.savefig('output/premium_fine_with_boundaries.png', dpi=150)
    plt.close()
    print('\n✅ Premium curves saved to output/premium_fine_with_boundaries.png')
    
    return df

if __name__ == '__main__':
    main()