#!/usr/bin/env python3
"""
Fix continuation calculation: continuation = risk‑neutral expectation of OPTION VALUES at next step,
not unwind values.
"""
import matplotlib
matplotlib.use('Agg')
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

def unwind_value(spot, time_to_expiry):
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    return black_scholes_call(spot, K, time_to_expiry, r, vol_high) - black_scholes_call(spot, K, time_to_expiry, r, vol_low)

def continuation_correct(spot, time):
    """
    Compute continuation value at (spot, time) using a TWO‑STEP tree:
    Step 1: compute option values at time+dt via backward induction over one more step.
    """
    # Build a small 2‑step tree from (time) to (time+2*dt)
    # We'll use the same dt as the lattice (T/n)
    # At time + 2*dt, option value = unwind value.
    # Then backward one step to get option values at time+dt.
    # Finally compute continuation = discounted expectation.
    
    # Possible spots after dt
    S_up = spot * u
    S_down = spot * d
    time_next = time + dt
    time_next2 = time + 2*dt
    
    # Unwind values at time+2*dt (maturity for this subtree)
    unwind_up_up = unwind_value(S_up * u, T - time_next2)
    unwind_up_down = unwind_value(S_up * d, T - time_next2)
    unwind_down_down = unwind_value(S_down * d, T - time_next2)
    
    # Option values at time+dt: max(unwind, continuation) where continuation is expectation of unwind at time+2*dt
    # For S_up node:
    continuation_up = np.exp(-r * dt) * (q * unwind_up_up + (1-q) * unwind_up_down)
    unwind_up = unwind_value(S_up, T - time_next)
    option_up = max(unwind_up, continuation_up)
    
    # For S_down node:
    continuation_down = np.exp(-r * dt) * (q * unwind_up_down + (1-q) * unwind_down_down)
    unwind_down = unwind_value(S_down, T - time_next)
    option_down = max(unwind_down, continuation_down)
    
    # Continuation at current node = discounted expectation of option values at time+dt
    continuation = np.exp(-r * dt) * (q * option_up + (1-q) * option_down)
    return continuation

def continuation_wrong(spot, time):
    """Wrong continuation: expectation of unwind values at next step."""
    S_up = spot * u
    S_down = spot * d
    time_next = time + dt
    unwind_up = unwind_value(S_up, T - time_next)
    unwind_down = unwind_value(S_down, T - time_next)
    return np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)

# Compare at S0, t=0
print("Continuation comparison at S0=100, t=0:")
print(f"Wrong continuation (expectation of unwind): {continuation_wrong(S0, 0):.6f}")
print(f"Correct continuation (expectation of option values): {continuation_correct(S0, 0):.6f}")
print(f"Unwind at t=0: {unwind_value(S0, T):.6f}")
print(f"Diff (unwind - wrong continuation): {unwind_value(S0, T) - continuation_wrong(S0, 0):.6f}")
print(f"Diff (unwind - correct continuation): {unwind_value(S0, T) - continuation_correct(S0, 0):.6f}")

# Compute boundary spot where unwind = correct continuation (root‑finding)
print("\nFinding boundary spot at t=0 (where unwind = correct continuation):")
spots = np.linspace(50, 150, 1001)
boundary_spot = None
for i in range(len(spots)-1):
    s1 = spots[i]
    s2 = spots[i+1]
    u1 = unwind_value(s1, T)
    c1 = continuation_correct(s1, 0)
    u2 = unwind_value(s2, T)
    c2 = continuation_correct(s2, 0)
    if (u1 - c1)*(u2 - c2) <= 0:
        boundary_spot = (s1 + s2)/2
        break
if boundary_spot:
    print(f"Boundary spot ≈ {boundary_spot:.2f}")
    print(f"At S0=100, we are {'above' if S0 >= boundary_spot else 'below'} boundary.")
else:
    print("No boundary found in range.")

# Plot unwind vs both continuation definitions
fig, ax = plt.subplots(figsize=(10,6))
unwind_vals = [unwind_value(s, T) for s in spots]
cont_wrong_vals = [continuation_wrong(s, 0) for s in spots]
cont_correct_vals = [continuation_correct(s, 0) for s in spots]
ax.plot(spots, unwind_vals, 'b-', label='Unwind value')
ax.plot(spots, cont_wrong_vals, 'r--', label='Continuation (wrong: expectation of unwind)')
ax.plot(spots, cont_correct_vals, 'g-.', label='Continuation (correct: expectation of option values)')
ax.axvline(S0, color='k', linestyle=':', label=f'S0={S0}')
if boundary_spot:
    ax.axvline(boundary_spot, color='m', linestyle='--', label=f'Boundary ≈ {boundary_spot:.1f}')
ax.set_xlabel('Spot')
ax.set_ylabel('Value')
ax.set_title('Unwind vs Continuation at t=0\nCorrect continuation accounts for optionality at next step')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/continuation_fixed.png', dpi=150)
plt.close()
print("\nPlot saved to output/continuation_fixed.png")