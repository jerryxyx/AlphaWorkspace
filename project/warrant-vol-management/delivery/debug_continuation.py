#!/usr/bin/env python3
"""
Debug continuation vs unwind for ATM case.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np

K = 100.0
S0 = 100.0
T = 1.0
r = 0.05
sigma_fair = 0.2
sigma_offset = 0.1
sigma_spot = 0.2  # equal

def sigma_fair_func(spot):
    return sigma_fair

# Use lattice with n=100 to get internal continuation values
n = 100
dt = T / n
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)

# Compute American values at time dt (step 1) for spots S0*u and S0*d
val_up, _, _ = lattice.binomial_tree_value(
    n-1, S0 * u, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
val_down, _, _ = lattice.binomial_tree_value(
    n-1, S0 * d, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
continuation_S0 = np.exp(-r * dt) * (q * val_up + (1 - q) * val_down)

# Unwind at S0, t=0
unwind_S0 = lattice.black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(S0, K, T, r, sigma_fair)

print(f"Spot S0 = {S0}")
print(f"Unwind value at t=0: {unwind_S0:.6f}")
print(f"Continuation value at t=0: {continuation_S0:.6f}")
print(f"Premium (unwind - continuation): {unwind_S0 - continuation_S0:.6f}")
print(f"Exercise? {unwind_S0 >= continuation_S0}")

# Now compute for a range of spots using lattice's boundary output
val, boundary, exercise = lattice.binomial_tree_value(
    n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
print(f"\nLattice results (n={n}):")
print(f"Initial value: {val:.6f}")
print(f"Boundary[0]: {boundary[0]:.2f}")
print(f"Exercise flags at step 0: {exercise[0]}")
# Spots at step 0: only one spot = S0
print(f"Spot at step 0: {S0}")

# Compute premium for spots around S0
spots = [90, 95, 100, 105, 110]
print("\nSpot | Unwind | Continuation | Premium | Exercise?")
print("-----|--------|--------------|---------|----------")
for s in spots:
    unwind = lattice.black_scholes_call(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
    # continuation via two-step expectation
    val_up, _, _ = lattice.binomial_tree_value(
        n-1, s * u, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    val_down, _, _ = lattice.binomial_tree_value(
        n-1, s * d, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    cont = np.exp(-r * dt) * (q * val_up + (1 - q) * val_down)
    prem = unwind - cont
    print(f"{s:4.0f} | {unwind:6.4f} | {cont:12.4f} | {prem:7.4f} | {unwind >= cont}")

# Check monotonicity of unwind and continuation separately
print("\n=== Unwind vs Spot ===")
for s in spots:
    unwind = lattice.black_scholes_call(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
    print(f"Spot {s}: unwind = {unwind:.4f}")

# Compute continuation using our earlier function (n_small=10) for comparison
def continuation_small(spot, tau, option_type='call', n_small=10):
    if tau <= 0:
        return 0.0
    dt = tau / n_small
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    q = (np.exp(r * dt) - d) / (u - d)
    val_up, _, _ = lattice.binomial_tree_value(
        n_small - 1, spot * u, K, tau - dt, r, sigma_spot, sigma_fair_func,
        sigma_offset, option_type=option_type)
    val_down, _, _ = lattice.binomial_tree_value(
        n_small - 1, spot * d, K, tau - dt, r, sigma_spot, sigma_fair_func,
        sigma_offset, option_type=option_type)
    return np.exp(-r * dt) * (q * val_up + (1 - q) * val_down)

print("\n=== Continuation with n_small=10 ===")
for s in spots:
    cont_small = continuation_small(s, T, 'call', 10)
    print(f"Spot {s}: continuation = {cont_small:.4f}")