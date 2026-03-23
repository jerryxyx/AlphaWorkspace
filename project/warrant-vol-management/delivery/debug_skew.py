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

# Skew: σ_fair(s) = a - b*(s - K)
a = 2.0
b = 0.01
def sigma_fair(s):
    return a - b * (s - K)

vol_low = sigma_fair(S0)
vol_high = vol_low + sigma_offset
print(f"S0={S0}, K={K}")
print(f"σ_fair = {vol_low}")
print(f"σ_high = {vol_high}")
print(f"σ_offset = {sigma_offset}")
price_low = black_scholes_call(S0, K, T, r, vol_low)
price_high = black_scholes_call(S0, K, T, r, vol_high)
print(f"Low‑vol call price: {price_low}")
print(f"High‑vol call price: {price_high}")
print(f"European unwind (t=0): {price_high - price_low}")

# Check one‑step binomial
dt = T / 200
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)
print(f"\ndt={dt}, u={u}, d={d}, q={q}")
S_up = S0 * u
S_down = S0 * d
print(f"S_up={S_up}, S_down={S_down}")
vol_low_up = sigma_fair(S_up)
vol_high_up = vol_low_up + sigma_offset
print(f"σ_fair(S_up)={vol_low_up}, σ_high(S_up)={vol_high_up}")
price_low_up = black_scholes_call(S_up, K, T-dt, r, vol_low_up)
price_high_up = black_scholes_call(S_up, K, T-dt, r, vol_high_up)
unwind_up = price_high_up - price_low_up
print(f"Up unwind: {unwind_up}")
vol_low_down = sigma_fair(S_down)
vol_high_down = vol_low_down + sigma_offset
print(f"σ_fair(S_down)={vol_low_down}, σ_high(S_down)={vol_high_down}")
price_low_down = black_scholes_call(S_down, K, T-dt, r, vol_low_down)
price_high_down = black_scholes_call(S_down, K, T-dt, r, vol_high_down)
unwind_down = price_high_down - price_low_down
print(f"Down unwind: {unwind_down}")
continuation = np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)
print(f"Continuation: {continuation}")
print(f"Unwind at t=0: {price_high - price_low}")
print(f"Diff: {continuation - (price_high - price_low)}")

# Run lattice with small n to inspect
import lattice
n = 10
val, boundary, flags = lattice.binomial_tree_value(
    n=n, S0=S0, K=K, T=T, r=r, sigma_spot=sigma_spot,
    sigma_fair_func=sigma_fair, sigma_offset=sigma_offset)
print(f"\nLattice n={n}: value={val}")
print(f"Boundary: {boundary}")
print(f"Flags length: {len(flags)}")
# Print first few nodes' values
# Let's manually compute a 2-step tree to verify
print("\nManual 2‑step tree (dt=0.5):")
dt2 = T / 2
u2 = np.exp(sigma_spot * np.sqrt(dt2))
d2 = 1.0 / u2
q2 = (np.exp(r * dt2) - d2) / (u2 - d2)
print(f"dt={dt2}, u={u2}, d={d2}, q={q2}")
# Time steps: t0, t1, t2
S = {}
S[(0,0)] = S0
S[(1,0)] = S0 * u2
S[(1,1)] = S0 * d2
S[(2,0)] = S[(1,0)] * u2
S[(2,1)] = S[(1,0)] * d2
S[(2,2)] = S[(1,1)] * d2
# Unwind values at t2
V = {}
for j in range(3):
    spot = S[(2,j)]
    vol_low = sigma_fair(spot)
    vol_high = vol_low + sigma_offset
    V[(2,j)] = black_scholes_call(spot, K, T-2*dt2, r, vol_high) - black_scholes_call(spot, K, T-2*dt2, r, vol_low)
print(f"t=2 values: {V[(2,0)]}, {V[(2,1)]}, {V[(2,2)]}")
# Backward to t1
for j in range(2):
    spot = S[(1,j)]
    unwind = black_scholes_call(spot, K, T-dt2, r, sigma_fair(spot)+sigma_offset) - black_scholes_call(spot, K, T-dt2, r, sigma_fair(spot))
    continuation = np.exp(-r * dt2) * (q2 * V[(2,j)] + (1-q2) * V[(2,j+1)])
    V[(1,j)] = max(unwind, continuation)
    print(f"t=1 spot={spot:.1f}: unwind={unwind:.3f}, cont={continuation:.3f}, value={V[(1,j)]:.3f}")
# t0
spot = S0
unwind0 = price_high - price_low
continuation0 = np.exp(-r * dt2) * (q2 * V[(1,0)] + (1-q2) * V[(1,1)])
value0 = max(unwind0, continuation0)
print(f"t=0 spot={spot}: unwind={unwind0:.3f}, cont={continuation0:.3f}, value={value0:.3f}")
print(f"2‑step lattice value: {value0}")