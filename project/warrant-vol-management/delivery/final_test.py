#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np
import lattice
import monte_carlo
import pde

print("Realistic test case with positive early‑exercise premium")
print("="*70)

# Parameters
K = 200.0
S0 = 100.0
sigma_offset = 0.15
sigma_spot = 0.2
T = 1.0
r = 0.05

# Volatility skew: decreasing with spot, bounded below by 0.1
def sigma_fair_skew(spot):
    raw = 0.5 - 0.002 * (spot - K)  # slope 0.002 per unit spot
    return max(0.1, raw)

print(f"K={K}, S0={S0}, σ_spot={sigma_spot}, σ_offset={sigma_offset}, r={r}, T={T}")
print(f"σ_fair(s) = max(0.1, 0.5 - 0.002*(s - {K}))")
print(f"σ_fair({S0}) = {sigma_fair_skew(S0):.3f}")
print(f"σ_fair({K}) = {sigma_fair_skew(K):.3f}")
print(f"σ_fair({300}) = {sigma_fair_skew(300):.3f}")
print()

# European unwind at t=0
vol_low0 = sigma_fair_skew(S0)
vol_high0 = vol_low0 + sigma_offset
price_low = black_scholes_call(S0, K, T, r, vol_low0)
price_high = black_scholes_call(S0, K, T, r, vol_high0)
european = price_high - price_low
print(f"European unwind at t=0: {european:.6f}")
print(f"  Low‑vol call (σ={vol_low0:.3f}): {price_low:.6f}")
print(f"  High‑vol call (σ={vol_high0:.3f}): {price_high:.6f}")
print()

# One‑step binomial to guess continuation vs unwind
dt = T / 200
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)
S_up = S0 * u
S_down = S0 * d
vol_low_up = sigma_fair_skew(S_up)
vol_high_up = vol_low_up + sigma_offset
unwind_up = black_scholes_call(S_up, K, T-dt, r, vol_high_up) - black_scholes_call(S_up, K, T-dt, r, vol_low_up)
vol_low_down = sigma_fair_skew(S_down)
vol_high_down = vol_low_down + sigma_offset
unwind_down = black_scholes_call(S_down, K, T-dt, r, vol_high_down) - black_scholes_call(S_down, K, T-dt, r, vol_low_down)
continuation = np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)
print(f"One‑step binomial:")
print(f"  Up spot={S_up:.2f}:   unwind={unwind_up:.6f} (σ_fair={vol_low_up:.3f})")
print(f"  Down spot={S_down:.2f}: unwind={unwind_down:.6f} (σ_fair={vol_low_down:.3f})")
print(f"  Continuation value = {continuation:.6f}")
print(f"  Difference (continuation - european) = {continuation - european:.6f}")
if continuation > european:
    print("  → Wait (early exercise NOT optimal)")
else:
    print("  → Unwind now (early exercise optimal)")
print()

# Run lattice
print("Lattice binomial tree (n=200):")
val_lat, boundary_lat, _ = lattice.binomial_tree_value(
    n=200,
    S0=S0,
    K=K,
    T=T,
    r=r,
    sigma_spot=sigma_spot,
    sigma_fair_func=sigma_fair_skew,
    sigma_offset=sigma_offset,
)
print(f"  Value: {val_lat:.6f}")
print(f"  Early‑exercise premium: {val_lat - european:.6f}")
finite = np.sum(np.isfinite(boundary_lat))
print(f"  Steps with exercise region: {finite} / {len(boundary_lat)}")
if finite > 0:
    print(f"  Boundary first 5: {boundary_lat[:5]}")
print()

# Monte Carlo LSM
print("Monte Carlo LSM (n_paths=10000, n_steps=50):")
val_mc, boundary_mc = monte_carlo.lsm_value(
    n_paths=10000,
    n_steps=50,
    S0=S0,
    K=K,
    T=T,
    r=r,
    sigma_spot=sigma_spot,
    sigma_fair_func=sigma_fair_skew,
    sigma_offset=sigma_offset,
)
print(f"  Value: {val_mc:.6f}")
print(f"  Early‑exercise premium: {val_mc - european:.6f}")
print(f"  Difference lattice vs MC: {abs(val_lat - val_mc):.6f}")
print()

# PDE (coarse grid)
print("PDE finite difference (n_S=100, n_t=100):")
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
    sigma_fair_func=sigma_fair_skew,
    sigma_offset=sigma_offset,
    method='implicit',
    omega=1.2,
    max_iter=100,
    tol=1e-6,
)
print(f"  Value: {val_pde:.6f}")
print(f"  Early‑exercise premium: {val_pde - european:.6f}")
print(f"  Difference lattice vs PDE: {abs(val_lat - val_pde):.6f}")
print()

# Summary
print("="*70)
print("SUMMARY")
print(f"European value:                 {european:.6f}")
print(f"Lattice (American):             {val_lat:.6f}  (premium {val_lat - european:.6f})")
print(f"Monte Carlo LSM (American):     {val_mc:.6f}  (premium {val_mc - european:.6f})")
print(f"PDE (American):                 {val_pde:.6f}  (premium {val_pde - european:.6f})")
print()
print("Agreement:")
print(f"  Lattice vs MC:  {abs(val_lat - val_mc):.6f}")
print(f"  Lattice vs PDE: {abs(val_lat - val_pde):.6f}")
print(f"  MC vs PDE:      {abs(val_mc - val_pde):.6f}")