#!/usr/bin/env python3
"""
Check boundary at maturity (time to expiry = 0) and one step before.
"""
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np

# Parameters
K = 200.0
S0 = 100.0
sigma_fair = 0.8
sigma_offset = 0.3
sigma_spot = 0.9
T = 1.0
r = 0.10
n = 200
dt = T / n
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)

def sigma_fair_func(spot):
    return sigma_fair

def unwind_value(spot, time_to_expiry):
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    return black_scholes_call(spot, K, time_to_expiry, r, vol_high) - black_scholes_call(spot, K, time_to_expiry, r, vol_low)

print("=== Boundary at maturity (time to expiry = 0) ===")
print("At maturity, both calls have payoff max(S-K,0).")
print("Thus spread payoff = 0 for all S.")
print("Unwind value at maturity = 0.")
print("Boundary spot? Not applicable because unwind = 0, continuation = N/A.")
print()

# One step before expiry (time = T - dt)
time_before = T - dt
print(f"=== One step before expiry (time = {time_before:.6f}) ===")
print(f"dt = {dt:.6f}")
print()

# Compute continuation value: discounted expectation of option values at maturity.
# Option values at maturity = unwind values at maturity = 0.
# Therefore continuation = 0.
continuation = 0.0
print(f"Continuation value (discounted expectation of maturity values) = {continuation:.6f}")
print()

# Compute unwind value for a range of spots
spots = [50, 100, 150, 200, 250, 300]
print("Spot | Unwind value | Unwind > Continuation?")
print("------|--------------|----------------------")
for s in spots:
    unwind = unwind_value(s, time_before)
    decision = "UNWIND" if unwind > continuation else "HOLD"
    print(f"{s:5.1f} | {unwind:12.6f} | {decision}")
print()

# Find boundary spot where unwind = continuation = 0
# Solve unwind(spot, time_before) = 0
# Since unwind value is positive for all spot? Let's see.
# Use root finding.
import matplotlib.pyplot as plt
spot_grid = np.linspace(50, 300, 1001)
unwind_grid = [unwind_value(s, time_before) for s in spot_grid]
# Find where unwind crosses zero
zero_crossings = []
for i in range(len(spot_grid)-1):
    if unwind_grid[i] * unwind_grid[i+1] <= 0:
        zero_crossings.append((spot_grid[i], spot_grid[i+1]))
if zero_crossings:
    print(f"Found {len(zero_crossings)} zero crossing(s) of unwind value.")
    for low, high in zero_crossings:
        print(f"  Between {low:.2f} and {high:.2f}")
else:
    print("No zero crossing found; unwind value stays positive (or negative) in range.")
print()

# Plot unwind vs spot
plt.figure(figsize=(10,6))
plt.plot(spot_grid, unwind_grid, 'b-', label='Unwind value at t=T-dt')
plt.axhline(0, color='k', linestyle='--', label='Continuation = 0')
plt.axvline(K, color='r', linestyle=':', label=f'K={K}')
plt.xlabel('Spot')
plt.ylabel('Unwind value')
plt.title(f'Unwind value one step before expiry (time to expiry = {dt:.4f})')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/unwind_one_step_before.png', dpi=150)
plt.close()
print("Plot saved to output/unwind_one_step_before.png")

# Also compute boundary using lattice function to see what it outputs
import lattice
val, boundary, flags = lattice.binomial_tree_value(
    n=200, S0=S0, K=K, T=T, r=r, sigma_spot=sigma_spot,
    sigma_fair_func=sigma_fair_func, sigma_offset=sigma_offset)
print("=== Lattice boundary (first 5 steps) ===")
for i in range(5):
    t = i * dt
    if boundary[i] == np.inf:
        print(f"step {i}, t={t:.3f}: boundary = INF (no exercise)")
    else:
        print(f"step {i}, t={t:.3f}: boundary = {boundary[i]:.2f}")
print()
print("At step n (maturity), boundary should be INF (no exercise region).")
print(f"boundary[{n}] = {boundary[n]}")
print()

# Check exercise flag at step n-1
print("=== Exercise flag at step n-1 (index n-1) ===")
if flags[n-1] is not None:
    spots_n1 = S0 * (u ** np.arange(n-1, -1, -1)) * (d ** np.arange(0, n-1+1))
    # spots_n1 are descending? Let's just see first few.
    print(f"First 10 spots at step n-1: {spots_n1[:10]}")
    print(f"First 10 exercise flags: {flags[n-1][:10]}")
    # Find where exercise is True
    ex_indices = np.where(flags[n-1])[0]
    if len(ex_indices) > 0:
        print(f"Exercise occurs at {len(ex_indices)} nodes.")
        print(f"Smallest spot where exercise: {spots_n1[ex_indices[0]]:.2f}")
        print(f"Largest spot where exercise: {spots_n1[ex_indices[-1]]:.2f}")
    else:
        print("No exercise at step n-1.")
else:
    print("flags[n-1] is None")