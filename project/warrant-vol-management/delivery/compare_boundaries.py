#!/usr/bin/env python3
"""
Compare exercise boundaries from lattice, PDE, and Monte Carlo.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import monte_carlo
import pde
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

# ---------- Helper: compute boundaries from premium array ----------
def boundaries_from_premium(spots, premium, tol=1e-9):
    """
    Return (lower, upper, zero_crossings) where lower/upper may be inf/-inf.
    """
    # Find zero‑crossings via linear interpolation
    zero_cross = []
    for k in range(len(spots) - 1):
        y0, y1 = premium[k], premium[k+1]
        if y0 * y1 <= 0:
            x0, x1 = spots[k], spots[k+1]
            if abs(y1 - y0) < tol:
                zero = (x0 + x1) / 2
            else:
                zero = x0 - y0 * (x1 - x0) / (y1 - y0)
            zero_cross.append(zero)
    
    if len(zero_cross) == 0:
        if all(p >= -tol for p in premium):
            lower = -np.inf
            upper = np.inf
        elif all(p <= tol for p in premium):
            lower = np.inf   # no exercise region
            upper = -np.inf
        else:
            lower = np.nan
            upper = np.nan
    elif len(zero_cross) == 1:
        z = zero_cross[0]
        # Determine which side is exercise region
        idx = np.where(spots > z)[0][0]
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
    
    return lower, upper, zero_cross

# ---------- Monte Carlo wrapper with option_type ----------
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
    Returns (value, boundary_array), where boundary_array[t] = min spot where exercise occurred.
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
    # Exercise boundary: minimum spot where exercise occurred at each step
    boundary = np.full(n_steps, np.inf)
    for t in range(n_steps):
        exercised = cashflow[:, t] == exercise_value[:, t]
        if np.any(exercised):
            boundary[t] = np.min(S[exercised, t])
    
    return value, boundary

# ---------- PDE wrapper with option_type ----------
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
    Returns (value, interp_func, exercise_boundary, S_grid, V).
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
    interp_func = interp1d(S_grid, V, kind='linear', bounds_error=False, fill_value='extrapolate')
    
    return value, interp_func, exercise_boundary, S_grid, V

# ---------- Main comparison ----------
def main():
    # Parameters (same as cross‑method validation)
    sigma_fair = 0.2
    K = 100.0
    S0 = 100.0
    T = 1.0
    r = 0.05
    sigma_offset_list = [0.0, 0.05]
    sigma_spot_list = [0.1, 0.5]
    option_types = ['call', 'put']
    
    # Spot grid for premium calculation (coarse but enough for boundaries)
    spot_grid = np.linspace(50, 150, 11)
    
    # Numerical settings (lightweight)
    lattice_n = 50
    mc_n_paths = 300
    mc_n_steps = 15
    pde_S_min = 1.0
    pde_S_max = 300.0
    pde_n_S = 80
    pde_n_t = 30
    
    sigma_fair_func = lambda s: sigma_fair
    
    rows = []
    
    total = len(sigma_spot_list) * len(sigma_offset_list) * len(option_types)
    count = 0
    
    for sigma_spot in sigma_spot_list:
        for sigma_offset in sigma_offset_list:
            for option_type in option_types:
                count += 1
                print(f'[{count}/{total}] σ_spot={sigma_spot:.2f}, σ_offset={sigma_offset:.2f}, {option_type}')
                
                # --- Lattice values across spot grid ---
                lattice_vals = []
                for spot in spot_grid:
                    amer, _, _ = lattice.binomial_tree_value(
                        lattice_n, spot, K, T, r, sigma_spot, sigma_fair_func,
                        sigma_offset, option_type=option_type)
                    lattice_vals.append(amer)
                lattice_vals = np.array(lattice_vals)
                
                # --- PDE values across spot grid ---
                _, pde_interp, pde_boundary, pde_S_grid, _ = pde_value_with_type(
                    pde_S_min, pde_S_max, pde_n_S, pde_n_t, S0, K, T, r, sigma_spot,
                    sigma_fair_func, sigma_offset, option_type=option_type)
                pde_vals = pde_interp(spot_grid)
                
                # --- Monte Carlo values across spot grid ---
                mc_vals = []
                for spot in spot_grid:
                    mc_val, _ = lsm_value_with_type(
                        mc_n_paths, mc_n_steps, spot, K, T, r, sigma_spot,
                        sigma_fair_func, sigma_offset, option_type=option_type)
                    mc_vals.append(mc_val)
                mc_vals = np.array(mc_vals)
                
                # --- Unwind (European spread) across spot grid ---
                if option_type == 'call':
                    unwind = lattice.black_scholes_call(spot_grid, K, T, r, sigma_fair + sigma_offset) - \
                             lattice.black_scholes_call(spot_grid, K, T, r, sigma_fair)
                else:
                    unwind = lattice.black_scholes_put(spot_grid, K, T, r, sigma_fair + sigma_offset) - \
                             lattice.black_scholes_put(spot_grid, K, T, r, sigma_fair)
                
                # --- Premium (unwind - continuation) for each method ---
                premium_lattice = unwind - lattice_vals
                premium_pde = unwind - pde_vals
                premium_mc = unwind - mc_vals
                
                # --- Boundaries via premium zero‑crossing ---
                lower_lat, upper_lat, zc_lat = boundaries_from_premium(spot_grid, premium_lattice)
                lower_pde, upper_pde, zc_pde = boundaries_from_premium(spot_grid, premium_pde)
                lower_mc, upper_mc, zc_mc = boundaries_from_premium(spot_grid, premium_mc)
                
                # --- Internal boundary from PDE (minimum exercise spot at t=0) ---
                _, _, pde_boundary_array, _, _ = pde_value_with_type(
                    pde_S_min, pde_S_max, pde_n_S, pde_n_t, S0, K, T, r, sigma_spot,
                    sigma_fair_func, sigma_offset, option_type=option_type)
                pde_internal_lower = pde_boundary_array[0] if not np.isinf(pde_boundary_array[0]) else np.nan
                
                # --- Internal boundary from MC (minimum exercise spot at t=0) ---
                _, mc_boundary_array = lsm_value_with_type(
                    mc_n_paths, mc_n_steps, S0, K, T, r, sigma_spot,
                    sigma_fair_func, sigma_offset, option_type=option_type)
                mc_internal_lower = mc_boundary_array[0] if not np.isinf(mc_boundary_array[0]) else np.nan
                
                rows.append({
                    'sigma_spot': sigma_spot,
                    'sigma_offset': sigma_offset,
                    'option_type': option_type,
                    # Lattice boundaries (premium)
                    'lower_boundary_lattice': lower_lat,
                    'upper_boundary_lattice': upper_lat,
                    'num_zero_crossings_lattice': len(zc_lat),
                    # PDE boundaries (premium)
                    'lower_boundary_pde': lower_pde,
                    'upper_boundary_pde': upper_pde,
                    'num_zero_crossings_pde': len(zc_pde),
                    # MC boundaries (premium)
                    'lower_boundary_mc': lower_mc,
                    'upper_boundary_mc': upper_mc,
                    'num_zero_crossings_mc': len(zc_mc),
                    # Internal boundaries (minimum exercise spot)
                    'pde_internal_lower': pde_internal_lower,
                    'mc_internal_lower': mc_internal_lower,
                })
    
    df = pd.DataFrame(rows)
    out_path = 'output/boundary_comparison.csv'
    df.to_csv(out_path, index=False)
    print(f'\n✅ Boundary comparison saved to {out_path}')
    
    # Print summary for finite‑interval cases
    finite = df[~np.isinf(df['lower_boundary_lattice']) & ~np.isinf(df['upper_boundary_lattice'])]
    print('\n=== Finite‑interval combos (lattice) ===')
    for _, row in finite.iterrows():
        print(f"σ_spot={row['sigma_spot']}, σ_offset={row['sigma_offset']}, {row['option_type']}")
        print(f"  Lattice: [{row['lower_boundary_lattice']:.2f}, {row['upper_boundary_lattice']:.2f}]")
        print(f"  PDE:     [{row['lower_boundary_pde']:.2f}, {row['upper_boundary_pde']:.2f}]")
        print(f"  MC:      [{row['lower_boundary_mc']:.2f}, {row['upper_boundary_mc']:.2f}]")
        print(f"  PDE internal lower: {row['pde_internal_lower']:.2f}")
        print(f"  MC internal lower:  {row['mc_internal_lower']:.2f}")
        print()
    
    return df

if __name__ == '__main__':
    main()