#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np

def test_scenario(name, K, S0, sigma_fair_func, sigma_offset, sigma_spot, r, T):
    """Return (unwind, continuation, diff, decision)"""
    vol_low = sigma_fair_func(S0)
    vol_high = vol_low + sigma_offset
    unwind0 = black_scholes_call(S0, K, T, r, vol_high) - black_scholes_call(S0, K, T, r, vol_low)
    dt = T / 200
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    q = (np.exp(r * dt) - d) / (u - d)
    S_up = S0 * u
    S_down = S0 * d
    vol_low_up = sigma_fair_func(S_up)
    vol_high_up = vol_low_up + sigma_offset
    unwind_up = black_scholes_call(S_up, K, T-dt, r, vol_high_up) - black_scholes_call(S_up, K, T-dt, r, vol_low_up)
    vol_low_down = sigma_fair_func(S_down)
    vol_high_down = vol_low_down + sigma_offset
    unwind_down = black_scholes_call(S_down, K, T-dt, r, vol_high_down) - black_scholes_call(S_down, K, T-dt, r, vol_low_down)
    continuation = np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)
    diff = continuation - unwind0
    return unwind0, continuation, diff, "WAIT" if diff > 0 else "UNWIND"

print("Searching for scenarios where waiting is optimal (continuation > unwind)")
print("="*70)

# Base parameters
T = 1.0
r = 0.05
sigma_spot = 0.2
sigma_offset = 0.15

scenarios = []

# 1. Deep ITM, constant vol
K = 200
S0 = 250
sigma_fair = 0.25
scenarios.append(("Deep ITM constant", K, S0, lambda s: sigma_fair, sigma_offset, sigma_spot, r, T))

# 2. ATM, constant vol
S0 = 200
scenarios.append(("ATM constant", K, S0, lambda s: sigma_fair, sigma_offset, sigma_spot, r, T))

# 3. Volatility smile: higher vol near K
def smile(spot, K=200, base=0.2, peak=0.4, width=50):
    return base + peak * np.exp(-(spot - K)**2 / (2 * width**2))
scenarios.append(("Smile (S0=100)", K, 100, lambda s: smile(s), sigma_offset, sigma_spot, r, T))
scenarios.append(("Smile (S0=200)", K, 200, lambda s: smile(s), sigma_offset, sigma_spot, r, T))

# 4. Volatility skew: decreasing with spot
def skew(spot, K=200, base=0.4, slope=0.002):
    return base - slope * (spot - K)
scenarios.append(("Skew (S0=100)", K, 100, lambda s: skew(s), sigma_offset, sigma_spot, r, T))

# 5. Extreme r
r_high = 0.20
scenarios.append(("High r=20%, ATM", K, 200, lambda s: 0.25, sigma_offset, sigma_spot, r_high, T))

# 6. Very short maturity
T_short = 0.1
scenarios.append(("Short T=0.1, ATM", K, 200, lambda s: 0.25, sigma_offset, sigma_spot, r, T_short))

# 7. Very long maturity
T_long = 5.0
scenarios.append(("Long T=5, ATM", K, 200, lambda s: 0.25, sigma_offset, sigma_spot, r, T_long))

# Run tests
for name, K, S0, sigma_func, offset, sigma_spot, r, T in scenarios:
    unwind, cont, diff, decision = test_scenario(name, K, S0, sigma_func, offset, sigma_spot, r, T)
    print(f"{name:25} S0={S0:5.0f} K={K:5.0f} σ_fair={sigma_func(S0):.3f} r={r:.2f} T={T:.1f}")
    print(f"  Unwind: {unwind:.6f}  Continuation: {cont:.6f}  Diff: {diff:.6f} → {decision}")
    print()

# If any scenario shows WAIT, run lattice to get premium
print("\n" + "="*70)
print("Running lattice for scenarios where diff > 0 (if any)...")
import lattice
for name, K, S0, sigma_func, offset, sigma_spot, r, T in scenarios:
    unwind, cont, diff, decision = test_scenario(name, K, S0, sigma_func, offset, sigma_spot, r, T)
    if diff > 1e-6:
        print(f"\n{name}:")
        val, boundary, _ = lattice.binomial_tree_value(
            n=100, S0=S0, K=K, T=T, r=r, sigma_spot=sigma_spot,
            sigma_fair_func=sigma_func, sigma_offset=offset)
        premium = val - unwind
        print(f"  Lattice value: {val:.6f}")
        print(f"  Early‑exercise premium: {premium:.6f}")
        finite = np.sum(np.isfinite(boundary))
        print(f"  Exercise region steps: {finite}/{len(boundary)}")