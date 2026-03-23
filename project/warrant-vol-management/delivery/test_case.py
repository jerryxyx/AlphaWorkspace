#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
import numpy as np
import lattice
import monte_carlo
import pde

# Parameters
K = 150.0
S0 = 100.0
sigma_fair = 0.25
sigma_spot = 0.2
sigma_offset = 0.15
T = 1.0
r = 0.05

print("Test Case: K=150, S0=100, sigma_fair=0.25, sigma_spot=0.2, sigma_offset=0.15")
print("="*70)

# European unwind value at t=0
from lattice import black_scholes_call
vol_low = sigma_fair
vol_high = sigma_fair + sigma_offset
price_low = black_scholes_call(S0, K, T, r, vol_low)
price_high = black_scholes_call(S0, K, T, r, vol_high)
european_diff = price_high - price_low
print(f"European unwind value (t=0): {european_diff:.6f}")
print(f"  Low‑vol call (σ={vol_low}): {price_low:.6f}")
print(f"  High‑vol call (σ={vol_high}): {price_high:.6f}")
print()

# Lattice with n=200
print("Lattice (n=200):")
val_lat, boundary_lat, flags = lattice.binomial_tree_value(
    n=200,
    S0=S0,
    K=K,
    T=T,
    r=r,
    sigma_spot=sigma_spot,
    sigma_fair_func=lambda s: sigma_fair,  # constant
    sigma_offset=sigma_offset,
)
print(f"  Value: {val_lat:.6f}")
print(f"  Early‑exercise premium: {val_lat - european_diff:.6f}")
print(f"  Boundary first 5 steps: {boundary_lat[:5]}")
# Count how many time steps have finite boundary
finite = np.sum(np.isfinite(boundary_lat))
print(f"  Steps with exercise region: {finite} / {len(boundary_lat)}")
print()

# Monte Carlo LSM (small for speed)
print("Monte Carlo LSM (n_paths=5000, n_steps=50):")
val_mc, boundary_mc = monte_carlo.lsm_value(
    n_paths=5000,
    n_steps=50,
    S0=S0,
    K=K,
    T=T,
    r=r,
    sigma_spot=sigma_spot,
    sigma_fair_func=lambda s: sigma_fair,
    sigma_offset=sigma_offset,
)
print(f"  Value: {val_mc:.6f}")
print(f"  Early‑exercise premium: {val_mc - european_diff:.6f}")
finite_mc = np.sum(np.isfinite(boundary_mc))
print(f"  Steps with exercise region: {finite_mc} / {len(boundary_mc)}")
print()

# PDE (coarse grid)
print("PDE (n_S=100, n_t=100):")
val_pde, _, boundary_pde = pde.pde_value(
    S_min=1.0,
    S_max=300.0,
    n_S=100,
    n_t=100,
    S0=S0,
    K=K,
    T=T,
    r=r,
    sigma_spot=sigma_spot,
    sigma_fair_func=lambda s: sigma_fair,
    sigma_offset=sigma_offset,
    method='implicit',
    omega=1.2,
    max_iter=100,
    tol=1e-6,
)
print(f"  Value: {val_pde:.6f}")
print(f"  Early‑exercise premium: {val_pde - european_diff:.6f}")
finite_pde = np.sum(np.isfinite(boundary_pde))
print(f"  Steps with exercise region: {finite_pde} / {len(boundary_pde)}")
print()

# Summary
print("="*70)
print("Summary:")
print(f"European: {european_diff:.6f}")
print(f"Lattice:  {val_lat:.6f} (diff {val_lat - european_diff:.6f})")
print(f"Monte Carlo: {val_mc:.6f} (diff {val_mc - european_diff:.6f})")
print(f"PDE:       {val_pde:.6f} (diff {val_pde - european_diff:.6f})")
print()
print("Lattice vs MC: {:.6f}".format(abs(val_lat - val_mc)))
print("Lattice vs PDE: {:.6f}".format(abs(val_lat - val_pde)))