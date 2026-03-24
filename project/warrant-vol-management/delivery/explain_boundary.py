#!/usr/bin/env python3
"""
Explain the exercise boundary: plot unwind vs continuation across spot at different times.
"""
import matplotlib
matplotlib.use('Agg')  # non‑interactive backend
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np
import matplotlib.pyplot as plt

# Extreme parameters
K = 200.0
S0 = 100.0
sigma_fair = 0.8
sigma_offset = 0.3
sigma_spot = 0.9
T = 1.0
r = 0.10
dt = T / 200
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)

def sigma_fair_func(spot):
    return sigma_fair

print("Exercise boundary analysis")
print("="*60)
print(f"Parameters: K={K}, S0={S0}, σ_fair={sigma_fair}, σ_offset={sigma_offset}, σ_spot={sigma_spot}, r={r}, T={T}")
print()

# Compute boundary from lattice (n=200)
import lattice
n = 200
val, boundary, flags = lattice.binomial_tree_value(
    n=n, S0=S0, K=K, T=T, r=r, sigma_spot=sigma_spot,
    sigma_fair_func=sigma_fair_func, sigma_offset=sigma_offset
)
print(f"Lattice value: {val:.6f}")
print(f"European unwind at t=0: {black_scholes_call(S0, K, T, r, sigma_fair+sigma_offset) - black_scholes_call(S0, K, T, r, sigma_fair):.6f}")
print(f"Early‑exercise premium: {val - (black_scholes_call(S0, K, T, r, sigma_fair+sigma_offset) - black_scholes_call(S0, K, T, r, sigma_fair)):.6f}")
print()
print("Boundary (first 10 steps):")
for i in range(10):
    t = i * dt
    print(f"  step {i}, t={t:.3f}: boundary={boundary[i]:.2f} {'(exercise region above)' if np.isfinite(boundary[i]) else '(no exercise)'}")

# Compute unwind and continuation across spot at t=0 and t=0.5
print("\n" + "="*60)
print("Unwind vs continuation across spot at t=0 and t=0.5")
spots = np.linspace(50, 200, 151)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

for idx, (time, ax) in enumerate(zip([0.0, 0.5], axes)):
    unwind_vals = []
    cont_vals = []
    for spot in spots:
        # Unwind value
        time_to_expiry = T - time
        vol_low = sigma_fair_func(spot)
        vol_high = vol_low + sigma_offset
        price_low = black_scholes_call(spot, K, time_to_expiry, r, vol_low)
        price_high = black_scholes_call(spot, K, time_to_expiry, r, vol_high)
        unwind = price_high - price_low
        unwind_vals.append(unwind)
        
        # Continuation value: one‑step binomial expectation
        # We'll use the same dt as the lattice (T/n)
        # Compute up/down spots
        S_up = spot * u
        S_down = spot * d
        time_next = time + dt
        vol_low_up = sigma_fair_func(S_up)
        vol_high_up = vol_low_up + sigma_offset
        unwind_up = black_scholes_call(S_up, K, T-time_next, r, vol_high_up) - black_scholes_call(S_up, K, T-time_next, r, vol_low_up)
        vol_low_down = sigma_fair_func(S_down)
        vol_high_down = vol_low_down + sigma_offset
        unwind_down = black_scholes_call(S_down, K, T-time_next, r, vol_high_down) - black_scholes_call(S_down, K, T-time_next, r, vol_low_down)
        continuation = np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)
        cont_vals.append(continuation)
    
    ax.plot(spots, unwind_vals, 'b-', label='Unwind value')
    ax.plot(spots, cont_vals, 'r--', label='Continuation value')
    # Find crossing where unwind >= continuation
    diff = np.array(unwind_vals) - np.array(cont_vals)
    # Find first index where diff >= 0
    crossing_idx = np.where(diff >= 0)[0]
    if len(crossing_idx) > 0:
        boundary_spot = spots[crossing_idx[0]]
        ax.axvline(boundary_spot, color='g', linestyle=':', label=f'Boundary ≈ {boundary_spot:.1f}')
        print(f"t={time:.1f}: boundary spot ≈ {boundary_spot:.1f}")
    ax.axvline(S0, color='k', linestyle='--', label=f'S0={S0}')
    ax.set_xlabel('Spot')
    ax.set_ylabel('Value')
    ax.set_title(f't = {time:.1f}')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output/boundary_crossing.png', dpi=150)
plt.close()
print("Plot saved to output/boundary_crossing.png")

# Interpret
print("\n" + "="*60)
print("INTERPRETATION")
print("1. Boundary exists (finite values) because for spots above a certain level,")
print("   unwind ≥ continuation → exercise is optimal.")
print("2. For spots below the boundary, continuation > unwind → waiting is better.")
print("3. At t=0, S0=100 is exactly at (or slightly above) the boundary,")
print("   so immediate unwinding is optimal → early‑exercise premium = 0.")
print("4. The boundary decreases over time (see boundary array) because as time passes,")
print("   the continuation value decays faster, making exercise optimal at lower spots.")
print()
print("Thus, the existence of an exercise region does NOT imply a positive premium")
print("at the root – it only means that for some spots/times, early exercise is")
print("optimal. At S0, we are already in that region, so no extra value from waiting.")