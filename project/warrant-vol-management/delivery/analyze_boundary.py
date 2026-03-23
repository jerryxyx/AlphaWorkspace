#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
import numpy as np
from lattice import black_scholes_call

# Parameters
K = 150.0
S0 = 100.0
sigma_fair = 0.25
sigma_spot = 0.2
sigma_offset = 0.15
T = 1.0
r = 0.05

print("Analyzing early‑exercise decisions")
print("="*60)

# Compute unwind value at t=0, t=0.5, t=0.9 for spot = S0
for t in [0.0, 0.5, 0.9]:
    time_to_expiry = T - t
    vol_low = sigma_fair
    vol_high = sigma_fair + sigma_offset
    price_low = black_scholes_call(S0, K, time_to_expiry, r, vol_low)
    price_high = black_scholes_call(S0, K, time_to_expiry, r, vol_high)
    unwind = price_high - price_low
    print(f"t={t:.1f}, time_to_expiry={time_to_expiry:.1f}: unwind = {unwind:.6f}")
print()

# Compute unwind for higher spot (e.g., 200)
for spot in [150.0, 200.0]:
    print(f"\nSpot = {spot}:")
    for t in [0.0, 0.5, 0.9]:
        time_to_expiry = T - t
        vol_low = sigma_fair
        vol_high = sigma_fair + sigma_offset
        price_low = black_scholes_call(spot, K, time_to_expiry, r, vol_low)
        price_high = black_scholes_call(spot, K, time_to_expiry, r, vol_high)
        unwind = price_high - price_low
        print(f"  t={t:.1f}: unwind = {unwind:.6f}")

# Now compute continuation value using a simple one‑step binomial
print("\n" + "="*60)
print("One‑step binomial continuation value at t=0, spot=S0")
dt = T / 200
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)
print(f"dt={dt:.4f}, u={u:.4f}, d={d:.4f}, q={q:.4f}")
# Up state spot
S_up = S0 * u
S_down = S0 * d
# Unwind values at t=dt
for S, label in [(S_up, "up"), (S_down, "down")]:
    time_to_expiry = T - dt
    price_low = black_scholes_call(S, K, time_to_expiry, r, sigma_fair)
    price_high = black_scholes_call(S, K, time_to_expiry, r, sigma_fair + sigma_offset)
    unwind = price_high - price_low
    print(f"  {label} spot={S:.2f}: unwind = {unwind:.6f}")
# Continuation value = discounted expectation
cont_up = black_scholes_call(S_up, K, T-dt, r, sigma_fair + sigma_offset) - black_scholes_call(S_up, K, T-dt, r, sigma_fair)
cont_down = black_scholes_call(S_down, K, T-dt, r, sigma_fair + sigma_offset) - black_scholes_call(S_down, K, T-dt, r, sigma_fair)
continuation = np.exp(-r * dt) * (q * cont_up + (1-q) * cont_down)
print(f"Continuation value = {continuation:.6f}")
# Unwind at t=0
unwind0 = black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - black_scholes_call(S0, K, T, r, sigma_fair)
print(f"Unwind at t=0      = {unwind0:.6f}")
print(f"Difference (continuation - unwind) = {continuation - unwind0:.6f}")