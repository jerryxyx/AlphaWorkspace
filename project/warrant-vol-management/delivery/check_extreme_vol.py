#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np

K = 200.0
S0 = 100.0
sigma_fair = 0.8
sigma_offset = 0.3
sigma_spot = 0.9
T = 1.0
r = 0.10

print("Extreme volatility scenario")
print(f"σ_fair={sigma_fair}, σ_spot={sigma_spot}, σ_offset={sigma_offset}")
print(f"K={K}, S0={S0}, r={r}, T={T}")
print("="*60)

vol_low = sigma_fair
vol_high = sigma_fair + sigma_offset
unwind0 = black_scholes_call(S0, K, T, r, vol_high) - black_scholes_call(S0, K, T, r, vol_low)
print(f"Unwind at t=0: {unwind0:.6f}")
print(f"  Low-vol call (σ={vol_low}): {black_scholes_call(S0, K, T, r, vol_low):.6f}")
print(f"  High-vol call (σ={vol_high}): {black_scholes_call(S0, K, T, r, vol_high):.6f}")
print()

# One-step binomial
dt = T / 200
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)
print(f"dt={dt:.4f}, u={u:.4f}, d={d:.4f}, q={q:.4f}")

S_up = S0 * u
S_down = S0 * d
unwind_up = black_scholes_call(S_up, K, T-dt, r, vol_high) - black_scholes_call(S_up, K, T-dt, r, vol_low)
unwind_down = black_scholes_call(S_down, K, T-dt, r, vol_high) - black_scholes_call(S_down, K, T-dt, r, vol_low)
continuation = np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)
print(f"Up state spot={S_up:.2f}:   unwind = {unwind_up:.6f}")
print(f"Down state spot={S_down:.2f}: unwind = {unwind_down:.6f}")
print(f"Continuation value = {continuation:.6f}")
print(f"Difference (continuation - unwind) = {continuation - unwind0:.6f}")
if continuation > unwind0:
    print("CONTINUATION > UNWIND → Wait (early exercise NOT optimal)")
else:
    print("CONTINUATION < UNWIND → Unwind now (early exercise optimal)")

# Check lattice
print("\n" + "="*60)
print("Running lattice (n=200)...")
import lattice
val, boundary, _ = lattice.binomial_tree_value(
    n=200,
    S0=S0,
    K=K,
    T=T,
    r=r,
    sigma_spot=sigma_spot,
    sigma_fair_func=lambda s: sigma_fair,
    sigma_offset=sigma_offset,
)
print(f"Lattice value: {val:.6f}")
print(f"Early‑exercise premium: {val - unwind0:.6f}")
finite = np.sum(np.isfinite(boundary))
print(f"Steps with exercise region: {finite} / {len(boundary)}")
print(f"Boundary first 5: {boundary[:5]}")