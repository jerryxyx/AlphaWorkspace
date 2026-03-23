#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np

K = 200.0
S0 = 100.0
sigma_offset = 0.15
sigma_spot = 0.2
T = 1.0
r = 0.05

# Volatility skew: σ_fair = 0.4 - 0.002*(spot - K)
def sigma_fair_skew(spot):
    return 0.4 - 0.002 * (spot - K)

print("Volatility skew scenario")
print("σ_fair(s) = 0.4 - 0.002*(s - K)")
print(f"σ_fair({S0}) = {sigma_fair_skew(S0):.3f}")
print(f"σ_fair({K}) = {sigma_fair_skew(K):.3f}")
print("="*60)

# Unwind at t=0
vol_low0 = sigma_fair_skew(S0)
vol_high0 = vol_low0 + sigma_offset
unwind0 = black_scholes_call(S0, K, T, r, vol_high0) - black_scholes_call(S0, K, T, r, vol_low0)
print(f"Unwind at t=0: {unwind0:.6f}")
print(f"  Low-vol σ={vol_low0:.3f}: {black_scholes_call(S0, K, T, r, vol_low0):.6f}")
print(f"  High-vol σ={vol_high0:.3f}: {black_scholes_call(S0, K, T, r, vol_high0):.6f}")
print()

# One-step binomial
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
print(f"Continuation value = {continuation:.6f}")
print(f"Difference (continuation - unwind) = {continuation - unwind0:.6f}")
if continuation > unwind0:
    print("CONTINUATION > UNWIND → Wait (early exercise NOT optimal)")
else:
    print("CONTINUATION < UNWIND → Unwind now (early exercise optimal)")

print("\n" + "="*60)
print("Check at higher spot levels:")
for spot in [150.0, 200.0]:
    vol_low = sigma_fair_skew(spot)
    vol_high = vol_low + sigma_offset
    unwind = black_scholes_call(spot, K, T, r, vol_high) - black_scholes_call(spot, K, T, r, vol_low)
    S_up = spot * u
    S_down = spot * d
    vol_low_up = sigma_fair_skew(S_up)
    vol_high_up = vol_low_up + sigma_offset
    up_val = black_scholes_call(S_up, K, T-dt, r, vol_high_up) - black_scholes_call(S_up, K, T-dt, r, vol_low_up)
    vol_low_down = sigma_fair_skew(S_down)
    vol_high_down = vol_low_down + sigma_offset
    down_val = black_scholes_call(S_down, K, T-dt, r, vol_high_down) - black_scholes_call(S_down, K, T-dt, r, vol_low_down)
    cont = np.exp(-r * dt) * (q * up_val + (1-q) * down_val)
    print(f"\nSpot={spot}:")
    print(f"  σ_fair={vol_low:.3f}, σ_high={vol_high:.3f}")
    print(f"  Unwind: {unwind:.6f}")
    print(f"  Continuation: {cont:.6f}")
    print(f"  Diff: {cont - unwind:.6f}")
    if cont > unwind:
        print("  → Wait")
    else:
        print("  → Unwind")