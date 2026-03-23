#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
import numpy as np
import lattice
import monte_carlo
import pde
import config

# Parameters
params = config.BASE_PARAMS
S0 = params['S0']
K = params['K']
T = params['T']
r = params['r']
sigma_spot = params['sigma_spot']
sigma_offset = params['sigma_offset']

# Volatility smile
def sigma_fair_smile(spot):
    rel = abs(np.log(spot / K))
    return 0.2 + 0.1 * rel

print("Volatility smile test")
print(f"sigma_fair({S0}) = {sigma_fair_smile(S0)}")
print(f"sigma_fair({50}) = {sigma_fair_smile(50)}")
print(f"sigma_fair({150}) = {sigma_fair_smile(150)}")
print()

# European difference
from lattice import black_scholes_call
vol_low = sigma_fair_smile(S0)
vol_high = vol_low + sigma_offset
price_low = black_scholes_call(S0, K, T, r, vol_low)
price_high = black_scholes_call(S0, K, T, r, vol_high)
european = price_high - price_low
print(f"European diff: {european}")
print()

# Lattice
print("Lattice (n=200)...")
val_lat, boundary_lat, _ = lattice.binomial_tree_value(
    n=200, S0=S0, K=K, T=T, r=r, sigma_spot=sigma_spot,
    sigma_fair_func=sigma_fair_smile, sigma_offset=sigma_offset
)
print(f"Value: {val_lat}")
print(f"Early exercise premium: {val_lat - european}")
print(f"Boundary finite: {boundary_lat[np.isfinite(boundary_lat)][:5]}")
print()

# Monte Carlo (small for speed)
print("Monte Carlo LSM (n_paths=5000, n_steps=50)...")
val_mc, boundary_mc = monte_carlo.lsm_value(
    n_paths=5000, n_steps=50, S0=S0, K=K, T=T, r=r, sigma_spot=sigma_spot,
    sigma_fair_func=sigma_fair_smile, sigma_offset=sigma_offset
)
print(f"Value: {val_mc}")
print(f"Early exercise premium: {val_mc - european}")
print(f"Boundary finite: {boundary_mc[np.isfinite(boundary_mc)][:5]}")
print()

# PDE (coarse grid)
print("PDE (n_S=100, n_t=100)...")
val_pde, _, boundary_pde = pde.pde_value(
    S_min=1.0, S_max=300.0, n_S=100, n_t=100,
    S0=S0, K=K, T=T, r=r, sigma_spot=sigma_spot,
    sigma_fair_func=sigma_fair_smile, sigma_offset=sigma_offset,
    method='implicit', omega=1.2, max_iter=100, tol=1e-6
)
print(f"Value: {val_pde}")
print(f"Early exercise premium: {val_pde - european}")
print(f"Boundary finite: {boundary_pde[np.isfinite(boundary_pde)][:5]}")
print()

# Summary
print("="*50)
print(f"European: {european}")
print(f"Lattice:  {val_lat} (diff {val_lat - european})")
print(f"Monte Carlo: {val_mc} (diff {val_mc - european})")
print(f"PDE:       {val_pde} (diff {val_pde - european})")
print(f"Lattice vs MC: {abs(val_lat - val_mc)}")
print(f"Lattice vs PDE: {abs(val_lat - val_pde)}")