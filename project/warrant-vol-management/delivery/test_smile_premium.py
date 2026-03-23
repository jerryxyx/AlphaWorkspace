#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np

K = 200.0
S0 = 100.0
sigma_offset = 0.3
sigma_spot = 0.9
T = 1.0
r = 0.10

# Volatility smile: quadratic in log-moneyness
# σ_fair(s) = base + a*(ln(s/K))^2
def sigma_fair_smile(spot, base=0.8, a=0.5):
    moneyness = np.log(spot / K)
    return base + a * moneyness**2

print("Volatility smile scenario")
print("σ_fair(s) = 0.8 + 0.5 * (ln(s/K))^2")
print(f"K={K}, S0={S0}")
print(f"σ_fair({S0}) = {sigma_fair_smile(S0):.4f}")
print(f"σ_fair({K}) = {sigma_fair_smile(K):.4f}")
print(f"σ_fair({50}) = {sigma_fair_smile(50):.4f}")
print(f"σ_fair({300}) = {sigma_fair_smile(300):.4f}")
print("="*60)

vol_low0 = sigma_fair_smile(S0)
vol_high0 = vol_low0 + sigma_offset
unwind0 = black_scholes_call(S0, K, T, r, vol_high0) - black_scholes_call(S0, K, T, r, vol_low0)
print(f"Unwind at t=0: {unwind0:.6f}")
print(f"  Low-vol call (σ={vol_low0:.3f}): {black_scholes_call(S0, K, T, r, vol_low0):.6f}")
print(f"  High-vol call (σ={vol_high0:.3f}): {black_scholes_call(S0, K, T, r, vol_high0):.6f}")
print()

# One-step binomial
dt = T / 200
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)
print(f"dt={dt:.4f}, u={u:.4f}, d={d:.4f}, q={q:.4f}")

S_up = S0 * u
S_down = S0 * d
vol_low_up = sigma_fair_smile(S_up)
vol_high_up = vol_low_up + sigma_offset
unwind_up = black_scholes_call(S_up, K, T-dt, r, vol_high_up) - black_scholes_call(S_up, K, T-dt, r, vol_low_up)
vol_low_down = sigma_fair_smile(S_down)
vol_high_down = vol_low_down + sigma_offset
unwind_down = black_scholes_call(S_down, K, T-dt, r, vol_high_down) - black_scholes_call(S_down, K, T-dt, r, vol_low_down)
continuation = np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)
print(f"Up state spot={S_up:.2f}:   unwind = {unwind_up:.6f} (σ_fair={vol_low_up:.3f})")
print(f"Down state spot={S_down:.2f}: unwind = {unwind_down:.6f} (σ_fair={vol_low_down:.3f})")
print(f"Continuation value = {continuation:.6f}")
print(f"Difference (continuation - unwind) = {continuation - unwind0:.6f}")
if continuation > unwind0 + 1e-8:
    print("CONTINUATION > UNWIND → Wait (early exercise NOT optimal)")
elif continuation < unwind0 - 1e-8:
    print("CONTINUATION < UNWIND → Unwind now (early exercise optimal)")
else:
    print("CONTINUATION ≈ UNWIND → Indifferent")

# Run lattice to get full American value
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
    sigma_fair_func=sigma_fair_smile,
    sigma_offset=sigma_offset,
)
print(f"Lattice value: {val:.6f}")
print(f"Early‑exercise premium: {val - unwind0:.6f}")
finite = np.sum(np.isfinite(boundary))
print(f"Steps with exercise region: {finite} / {len(boundary)}")
if finite > 0:
    print(f"Boundary first 5: {boundary[:5]}")

# Also check Monte Carlo LSM (small)
print("\n" + "="*60)
print("Running Monte Carlo LSM (n_paths=5000, n_steps=50)...")
import monte_carlo
val_mc, boundary_mc = monte_carlo.lsm_value(
    n_paths=5000,
    n_steps=50,
    S0=S0,
    K=K,
    T=T,
    r=r,
    sigma_spot=sigma_spot,
    sigma_fair_func=sigma_fair_smile,
    sigma_offset=sigma_offset,
)
print(f"Monte Carlo value: {val_mc:.6f}")
print(f"Early‑exercise premium (MC): {val_mc - unwind0:.6f}")
print(f"Difference lattice vs MC: {abs(val - val_mc):.6f}")