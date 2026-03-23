#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np

K = 200.0
S0 = 100.0
sigma_fair = 0.25
sigma_offset = 0.15
sigma_spot = 0.2
T = 1.0
r = 0.10  # 10% interest rate

print("High interest rate scenario: r = 10%, K = 200")
print("="*60)

# European unwind at t=0
vol_low = sigma_fair
vol_high = sigma_fair + sigma_offset
price_low = black_scholes_call(S0, K, T, r, vol_low)
price_high = black_scholes_call(S0, K, T, r, vol_high)
unwind0 = price_high - price_low
print(f"European unwind at t=0: {unwind0:.6f}")
print(f"  Low-vol call (σ={vol_low}): {price_low:.6f}")
print(f"  High-vol call (σ={vol_high}): {price_high:.6f}")
print()

# One-step binomial to estimate continuation value
dt = T / 200  # small step
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)
print(f"dt={dt:.4f}, u={u:.4f}, d={d:.4f}, q={q:.4f}")

S_up = S0 * u
S_down = S0 * d

# Unwind values at t=dt
unwind_up = black_scholes_call(S_up, K, T-dt, r, vol_high) - black_scholes_call(S_up, K, T-dt, r, vol_low)
unwind_down = black_scholes_call(S_down, K, T-dt, r, vol_high) - black_scholes_call(S_down, K, T-dt, r, vol_low)
print(f"Up state spot={S_up:.2f}:   unwind = {unwind_up:.6f}")
print(f"Down state spot={S_down:.2f}: unwind = {unwind_down:.6f}")

continuation = np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)
print(f"Continuation value (discounted expectation) = {continuation:.6f}")
print(f"Unwind at t=0 = {unwind0:.6f}")
print(f"Difference (continuation - unwind) = {continuation - unwind0:.6f}")
print()

# Decision
if continuation > unwind0:
    print("CONTINUATION > UNWIND → Wait (early exercise NOT optimal)")
elif continuation < unwind0:
    print("CONTINUATION < UNWIND → Unwind now (early exercise optimal)")
else:
    print("CONTINUATION = UNWIND → Indifferent")

# Also compute for higher spot values
print("\n" + "="*60)
print("Check at higher spot levels (S=150, S=200):")
for spot in [150.0, 200.0]:
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