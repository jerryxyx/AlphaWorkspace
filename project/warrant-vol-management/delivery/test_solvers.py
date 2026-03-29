#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""
Test that lattice, PDE, and Monte Carlo solvers produce similar results
for a range of parameters.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import pde
import monte_carlo

def test_basic():
    """Basic test with constant volatility."""
    sigma_fair = 0.2
    K = 100.0
    S0 = 100.0
    T = 1.0
    r = 0.05
    sigma_spot = 0.2
    sigma_offset = 0.1
    sigma_fair_func = lambda s: sigma_fair
    
    # Lattice
    n_t = 100
    val_lat, ex_lat, cont_lat = lattice.binomial_tree_value(
        n_t, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call'
    )
    print(f"Lattice: value={val_lat:.6f}, exercise={ex_lat:.6f}, continuation={cont_lat:.6f}, premium={ex_lat - cont_lat:.6f}")
    
    # PDE
    S_min = 1.0
    S_max = 300.0
    n_S = 200
    val_pde, ex_pde, cont_pde = pde.pde_value(
        S_min, S_max, n_S, n_t, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset,
        option_type='call'
    )
    print(f"PDE:     value={val_pde:.6f}, exercise={ex_pde:.6f}, continuation={cont_pde:.6f}, premium={ex_pde - cont_pde:.6f}")
    
    # Monte Carlo
    n_paths = 20000
    val_mc, ex_mc, cont_mc = monte_carlo.lsm_value(
        n_paths, n_t, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset,
        option_type='call'
    )
    print(f"MC:      value={val_mc:.6f}, exercise={ex_mc:.6f}, continuation={cont_mc:.6f}, premium={ex_mc - cont_mc:.6f}")
    
    # Differences
    print("\nDifferences (absolute):")
    print(f"Lattice - PDE value: {val_lat - val_pde:.6f}")
    print(f"Lattice - MC value:  {val_lat - val_mc:.6f}")
    print(f"PDE - MC value:      {val_pde - val_mc:.6f}")
    print(f"Exercise value diff (Lattice - PDE): {ex_lat - ex_pde:.6f}")
    print(f"Continuation value diff (Lattice - PDE): {cont_lat - cont_pde:.6f}")
    
    # Tolerances
    tol_value = 0.01
    tol_exercise = 1e-3  # numerical discretization/interpolation across methods
    tol_continuation = 0.02
    assert abs(val_lat - val_pde) < tol_value, f"Lattice-PDE value mismatch: {val_lat - val_pde}"
    assert abs(val_lat - val_mc) < tol_value, f"Lattice-MC value mismatch: {val_lat - val_mc}"
    assert abs(ex_lat - ex_pde) < tol_exercise, f"Exercise value mismatch"
    assert abs(cont_lat - cont_pde) < tol_continuation, f"Continuation value mismatch"
    print("\nAll checks passed within tolerance.")

def test_put_spread():
    """Test put spread."""
    sigma_fair = 0.2
    K = 100.0
    S0 = 100.0
    T = 1.0
    r = 0.05
    sigma_spot = 0.2
    sigma_offset = 0.1
    sigma_fair_func = lambda s: sigma_fair
    
    # Lattice
    n_t = 100
    val_lat, ex_lat, cont_lat = lattice.binomial_tree_value(
        n_t, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put'
    )
    print(f"Put Lattice: value={val_lat:.6f}, exercise={ex_lat:.6f}, continuation={cont_lat:.6f}, premium={ex_lat - cont_lat:.6f}")
    
    # PDE
    S_min = 1.0
    S_max = 300.0
    n_S = 200
    val_pde, ex_pde, cont_pde = pde.pde_value(
        S_min, S_max, n_S, n_t, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset,
        option_type='put'
    )
    print(f"Put PDE:     value={val_pde:.6f}, exercise={ex_pde:.6f}, continuation={cont_pde:.6f}, premium={ex_pde - cont_pde:.6f}")
    
    # Monte Carlo
    n_paths = 20000
    val_mc, ex_mc, cont_mc = monte_carlo.lsm_value(
        n_paths, n_t, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset,
        option_type='put'
    )
    print(f"Put MC:      value={val_mc:.6f}, exercise={ex_mc:.6f}, continuation={cont_mc:.6f}, premium={ex_mc - cont_mc:.6f}")
    
    # Differences
    print("\nPut spread differences:")
    print(f"Lattice - PDE value: {val_lat - val_pde:.6f}")
    print(f"Lattice - MC value:  {val_lat - val_mc:.6f}")
    tol = 0.01
    assert abs(val_lat - val_pde) < tol
    assert abs(val_lat - val_mc) < tol
    print("Put spread checks passed.")

if __name__ == "__main__":
    print("=== Testing call spread ===")
    test_basic()
    print("\n=== Testing put spread ===")
    test_put_spread()