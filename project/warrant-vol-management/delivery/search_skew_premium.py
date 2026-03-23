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
dt = T / 200
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)

print("Searching for skew parameters where continuation > unwind")
print("σ_fair(s) = a - b*(s - K)")
print("="*70)

results = []
for a in np.linspace(0.5, 2.0, 16):
    for b in np.linspace(0.0, 0.01, 11):
        if b == 0:
            continue
        def sigma_fair(s):
            return a - b * (s - K)
        vol_low0 = sigma_fair(S0)
        vol_high0 = vol_low0 + sigma_offset
        unwind0 = black_scholes_call(S0, K, T, r, vol_high0) - black_scholes_call(S0, K, T, r, vol_low0)
        S_up = S0 * u
        S_down = S0 * d
        vol_low_up = sigma_fair(S_up)
        vol_high_up = vol_low_up + sigma_offset
        unwind_up = black_scholes_call(S_up, K, T-dt, r, vol_high_up) - black_scholes_call(S_up, K, T-dt, r, vol_low_up)
        vol_low_down = sigma_fair(S_down)
        vol_high_down = vol_low_down + sigma_offset
        unwind_down = black_scholes_call(S_down, K, T-dt, r, vol_high_down) - black_scholes_call(S_down, K, T-dt, r, vol_low_down)
        continuation = np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)
        diff = continuation - unwind0
        if diff > 1e-6:
            results.append((a, b, diff, unwind0, continuation))
            print(f"a={a:.3f}, b={b:.5f}: diff={diff:.6f}, unwind={unwind0:.3f}, cont={continuation:.3f}")

if not results:
    print("No skew found with continuation > unwind.")
else:
    print(f"\nFound {len(results)} skew(s) with positive diff.")
    # Take the best one
    best = max(results, key=lambda x: x[2])
    a, b, diff, unwind0, continuation = best
    print(f"\nBest skew: a={a:.3f}, b={b:.5f}")
    print(f"Unwind at t=0: {unwind0:.6f}")
    print(f"Continuation:   {continuation:.6f}")
    print(f"Diff: {diff:.6f}")
    # Run lattice
    import lattice
    val, boundary, _ = lattice.binomial_tree_value(
        n=200,
        S0=S0,
        K=K,
        T=T,
        r=r,
        sigma_spot=sigma_spot,
        sigma_fair_func=lambda s: a - b * (s - K),
        sigma_offset=sigma_offset,
    )
    print(f"\nLattice value: {val:.6f}")
    print(f"Early‑exercise premium: {val - unwind0:.6f}")
    finite = np.sum(np.isfinite(boundary))
    print(f"Exercise region steps: {finite}/{len(boundary)}")
    if finite < len(boundary):
        print("Some steps have NO exercise region → waiting may be optimal there.")