#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np

K = 200.0
S0 = 200.0  # ATM
sigma_fair = 0.25
sigma_offset = 0.15
sigma_spot = 0.2
T = 1.0
r = 0.05

print("ATM scenario: S0 = K = 200")
print("σ_fair=0.25, σ_offset=0.15")
print("="*60)

vol_low = sigma_fair
vol_high = sigma_fair + sigma_offset
unwind0 = black_scholes_call(S0, K, T, r, vol_high) - black_scholes_call(S0, K, T, r, vol_low)
print(f"Unwind at t=0: {unwind0:.6f}")
print(f"  Low-vol call: {black_scholes_call(S0, K, T, r, vol_low):.6f}")
print(f"  High-vol call: {black_scholes_call(S0, K, T, r, vol_high):.6f}")
print()

# One-step binomial
dt = T / 200
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)
S_up = S0 * u
S_down = S0 * d
unwind_up = black_scholes_call(S_up, K, T-dt, r, vol_high) - black_scholes_call(S_up, K, T-dt, r, vol_low)
unwind_down = black_scholes_call(S_down, K, T-dt, r, vol_high) - black_scholes_call(S_down, K, T-dt, r, vol_low)
continuation = np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)
print(f"Continuation value = {continuation:.6f}")
print(f"Difference (continuation - unwind) = {continuation - unwind0:.6f}")
if continuation > unwind0:
    print("CONTINUATION > UNWIND → Wait (early exercise NOT optimal)")
else:
    print("CONTINUATION < UNWIND → Unwind now (early exercise optimal)")

# Also compute for a range of spots
print("\n" + "="*60)
print("Check for various spot levels (same vol):")
for spot in [180.0, 200.0, 220.0]:
    unwind = black_scholes_call(spot, K, T, r, vol_high) - black_scholes_call(spot, K, T, r, vol_low)
    S_up = spot * u
    S_down = spot * d
    up_val = black_scholes_call(S_up, K, T-dt, r, vol_high) - black_scholes_call(S_up, K, T-dt, r, vol_low)
    down_val = black_scholes_call(S_down, K, T-dt, r, vol_high) - black_scholes_call(S_down, K, T-dt, r, vol_low)
    cont = np.exp(-r * dt) * (q * up_val + (1-q) * down_val)
    print(f"\nSpot={spot}:")
    print(f"  Unwind: {unwind:.6f}")
    print(f"  Continuation: {cont:.6f}")
    print(f"  Diff: {cont - unwind:.6f}")
    if cont > unwind:
        print("  → Wait")
    else:
        print("  → Unwind")