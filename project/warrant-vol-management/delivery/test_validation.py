#!/usr/bin/env python3
"""
Validation tests for lattice method.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import monte_carlo
import numpy as np

def test_european_limit():
    """
    If early exercise is never optimal, American value should equal European value.
    We can test by setting sigma_offset = 0 (identical options) => value = 0.
    """
    n = 200
    S0 = 100.0
    K = 100.0
    T = 1.0
    r = 0.05
    sigma_spot = 0.2
    sigma_fair_func = lambda s: 0.2
    sigma_offset = 0.0
    
    val, boundary, flags = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset
    )
    print(f"Lattice value with zero offset: {val}")
    assert abs(val) < 1e-10, f"Value should be zero, got {val}"
    print("PASS: zero offset gives zero value.")
    
    # Small offset, but maybe early exercise not optimal? We'll compute European difference.
    sigma_offset = 0.1
    # European difference at time 0:
    vol_low = sigma_fair_func(S0)
    vol_high = vol_low + sigma_offset
    from lattice import black_scholes_call
    price_low = black_scholes_call(S0, K, T, r, vol_low)
    price_high = black_scholes_call(S0, K, T, r, vol_high)
    european_diff = price_high - price_low
    print(f"European difference: {european_diff}")
    
    # Lattice value should be >= european_diff (early exercise premium)
    val, boundary, flags = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset
    )
    print(f"Lattice American value: {val}")
    print(f"Early exercise premium: {val - european_diff}")
    assert val >= european_diff - 1e-10, "American value should be at least European"
    
    # Check that boundary is finite (some exercise region)
    if np.any(np.isfinite(boundary)):
        print(f"Exercise boundary exists: {boundary[np.isfinite(boundary)]}")
    else:
        print("No exercise boundary (never optimal to unwind).")
    
    # Compare with Monte Carlo LSM (coarse)
    mc_val, mc_boundary = monte_carlo.lsm_value(
        n_paths=5000,
        n_steps=50,
        S0=S0, K=K, T=T, r=r,
        sigma_spot=sigma_spot,
        sigma_fair_func=sigma_fair_func,
        sigma_offset=sigma_offset,
    )
    print(f"Monte Carlo LSM value: {mc_val}")
    diff = abs(val - mc_val)
    print(f"Difference lattice vs MC: {diff}")
    # tolerance relaxed due to Monte Carlo error
    assert diff < 0.2, f"Difference too large: {diff}"
    print("PASS: lattice and MC within tolerance.")
    
    return True

if __name__ == "__main__":
    test_european_limit()