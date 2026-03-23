#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np

K = 200.0
S0 = 100.0
sigma_fair = 0.25
sigma_offset = 0.15
sigma_spot = 0.2
T = 1.0
r = 0.10

print("High r lattice (n=200)")
print("Parameters: K=200, S0=100, r=10%, σ_fair=0.25, σ_offset=0.15")
print("="*60)

val, boundary, flags = lattice.binomial_tree_value(
    n=200,
    S0=S0,
    K=K,
    T=T,
    r=r,
    sigma_spot=sigma_spot,
    sigma_fair_func=lambda s: sigma_fair,
    sigma_offset=sigma_offset,
)

# European benchmark
from lattice import black_scholes_call
vol_low = sigma_fair
vol_high = sigma_fair + sigma_offset
price_low = black_scholes_call(S0, K, T, r, vol_low)
price_high = black_scholes_call(S0, K, T, r, vol_high)
european = price_high - price_low

print(f"European unwind: {european:.6f}")
print(f"Lattice value:   {val:.6f}")
print(f"Early‑exercise premium: {val - european:.6f}")
print(f"Boundary first 5 steps: {boundary[:5]}")
finite = np.sum(np.isfinite(boundary))
print(f"Steps with exercise region: {finite} / {len(boundary)}")

# Check if any step has continuation > unwind at S0
print("\nChecking decision at each time step (spot=S0):")
dt = T / 200
for i in range(0, min(5, len(boundary))):
    t = i * dt
    time_to_expiry = T - t
    unwind = black_scholes_call(S0, K, time_to_expiry, r, vol_high) - black_scholes_call(S0, K, time_to_expiry, r, vol_low)
    if boundary[i] <= S0:
        decision = "UNWIND"
    else:
        decision = "WAIT"
    print(f"Step {i}, t={t:.3f}: unwind={unwind:.6f}, boundary={boundary[i]:.2f} → {decision}")