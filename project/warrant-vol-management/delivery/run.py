#!/usr/bin/env python3
"""
Main driver for pricing the arbitrage derivative using three numerical methods.
"""
import sys
sys.path.insert(0, 'src')

import numpy as np
import matplotlib.pyplot as plt
import config
import lattice
import monte_carlo
import pde

def run_lattice(params, lattice_params):
    """Run lattice method."""
    val, boundary, flags = lattice.binomial_tree_value(
        n=lattice_params['n'],
        S0=params['S0'],
        K=params['K'],
        T=params['T'],
        r=params['r'],
        sigma_spot=params['sigma_spot'],
        sigma_fair_func=config.sigma_fair_constant,
        sigma_offset=params['sigma_offset'],
    )
    return val, boundary, flags

def run_monte_carlo(params, mc_params):
    """Run Monte Carlo LSM."""
    val, boundary = monte_carlo.lsm_value(
        n_paths=mc_params['n_paths'],
        n_steps=mc_params['n_steps'],
        S0=params['S0'],
        K=params['K'],
        T=params['T'],
        r=params['r'],
        sigma_spot=params['sigma_spot'],
        sigma_fair_func=config.sigma_fair_constant,
        sigma_offset=params['sigma_offset'],
        basis_funcs=mc_params['basis_funcs'],
    )
    return val, boundary

def run_pde(params, pde_params):
    """Run PDE finite difference."""
    val, grid_values, boundary = pde.pde_value(
        S_min=pde_params['S_min'],
        S_max=pde_params['S_max'],
        n_S=pde_params['n_S'],
        n_t=pde_params['n_t'],
        S0=params['S0'],
        K=params['K'],
        T=params['T'],
        r=params['r'],
        sigma_spot=params['sigma_spot'],
        sigma_fair_func=config.sigma_fair_constant,
        sigma_offset=params['sigma_offset'],
        method=pde_params['method'],
    )
    return val, grid_values, boundary

def main():
    params = config.BASE_PARAMS
    lattice_params = config.LATTICE_PARAMS
    mc_params = config.MC_PARAMS
    pde_params = config.PDE_PARAMS
    
    print("=" * 60)
    print("Arbitrage Derivative Valuation")
    print("=" * 60)
    print(f"Parameters: S0={params['S0']}, K={params['K']}, T={params['T']}, r={params['r']}, sigma_spot={params['sigma_spot']}, sigma_offset={params['sigma_offset']}")
    print()
    
    # Lattice
    print("[Lattice Binomial Tree]")
    val_lattice, boundary_lattice, _ = run_lattice(params, lattice_params)
    print(f"Value: {val_lattice}")
    print(f"Exercise boundary (first 10 steps): {boundary_lattice[:10]}")
    print()
    
    # Monte Carlo
    print("[Monte Carlo LSM]")
    val_mc, boundary_mc = run_monte_carlo(params, mc_params)
    print(f"Value: {val_mc}")
    print(f"Exercise boundary (first 10 steps): {boundary_mc[:10]}")
    print()
    
    # PDE (placeholder)
    print("[PDE Finite Difference]")
    val_pde, _, boundary_pde = run_pde(params, pde_params)
    print(f"Value: {val_pde}")
    print(f"Exercise boundary (first 10 steps): {boundary_pde[:10]}")
    print()
    
    # Comparison
    print("=" * 60)
    print("Comparison")
    print(f"Lattice vs MC difference: {abs(val_lattice - val_mc)}")
    print(f"Lattice vs PDE difference: {abs(val_lattice - val_pde)}")
    print()
    
    # Plot exercise boundaries
    time_steps = np.arange(len(boundary_lattice))
    plt.figure(figsize=(10,6))
    plt.plot(time_steps, boundary_lattice, 'o-', label='Lattice', markersize=4)
    plt.plot(time_steps[:len(boundary_mc)], boundary_mc, 's-', label='Monte Carlo', markersize=4)
    plt.plot(time_steps[:len(boundary_pde)], boundary_pde, '^-', label='PDE', markersize=4)
    plt.xlabel('Time Step')
    plt.ylabel('Spot Boundary (exercise above)')
    plt.title('Exercise Boundary Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig('output/exercise_boundary.png', dpi=150)
    plt.close()
    print("Plot saved to output/exercise_boundary.png")
    
    # Save results to CSV
    import pandas as pd
    df = pd.DataFrame({
        'time_step': time_steps,
        'boundary_lattice': boundary_lattice,
        'boundary_mc': np.pad(boundary_mc, (0, len(time_steps)-len(boundary_mc)), constant_values=np.nan),
        'boundary_pde': np.pad(boundary_pde, (0, len(time_steps)-len(boundary_pde)), constant_values=np.nan),
    })
    df.to_csv('output/boundary_comparison.csv', index=False)
    print("CSV saved to output/boundary_comparison.csv")
    
    # Compute European benchmark
    from lattice import black_scholes_call
    vol_low = config.sigma_fair_constant(params['S0'])
    vol_high = vol_low + params['sigma_offset']
    price_low = black_scholes_call(params['S0'], params['K'], params['T'], params['r'], vol_low)
    price_high = black_scholes_call(params['S0'], params['K'], params['T'], params['r'], vol_high)
    european_diff = price_high - price_low
    print(f"\nEuropean difference (no early exercise): {european_diff}")
    print(f"Early exercise premium (Lattice): {val_lattice - european_diff}")
    print(f"Early exercise premium (MC): {val_mc - european_diff}")
    print(f"Early exercise premium (PDE): {val_pde - european_diff}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())