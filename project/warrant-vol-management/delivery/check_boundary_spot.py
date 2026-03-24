#!/usr/bin/env python3
"""
Check that boundary[i] is the smallest spot where exercise is optimal.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np

def constant_sigma(spot):
    return 0.2

# Parameters where exercise region is not the whole grid
S0 = 100.0
K = 100.0
T = 1.0
r = 0.05
sigma_spot = 0.2
sigma_offset = 0.1
n = 5  # small tree for visibility

val, boundary, exercise = lattice.binomial_tree_value(
    n, S0, K, T, r, sigma_spot, constant_sigma, sigma_offset)

print("=== Lattice with n=5 ===")
print(f"Initial value: {val:.6f}")
print()

# Show spots and exercise flags for each time step
for i in range(n+1):
    # Reconstruct spots for this time step (same as inside lattice)
    dt = T / n
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    spots = S0 * (u ** np.arange(i, -1, -1)) * (d ** np.arange(0, i+1))
    ex = exercise[i]
    print(f"Step {i}, t={i*dt:.3f}:")
    print(f"  Spots ({len(spots)}): {spots.round(2)}")
    print(f"  Exercise flags: {ex}")
    if np.any(ex):
        print(f"  Smallest spot where exercise True: {np.min(spots[ex]):.2f}")
        print(f"  Boundary[{i}] = {boundary[i]:.2f}")
        # Verify equality except at maturity (i=n) where boundary is inf
        if i != n:
            assert np.abs(boundary[i] - np.min(spots[ex])) < 1e-10, f"Mismatch at step {i}"
        else:
            print("  (at maturity, boundary is inf by design)")
    else:
        print(f"  No exercise -> boundary[{i}] = {boundary[i]}")
    print()

# Also check ordering of spots
print("Spot ordering at each step:")
for i in range(n+1):
    dt = T / n
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    spots = S0 * (u ** np.arange(i, -1, -1)) * (d ** np.arange(0, i+1))
    is_descending = all(spots[j] >= spots[j+1] for j in range(len(spots)-1))
    print(f"Step {i}: descending? {is_descending}, first={spots[0]:.2f}, last={spots[-1]:.2f}")

# Test with a case where exercise is False at t=0
print("\n=== Case where S0 is below boundary (exercise False at t=0) ===")
# Use lower S0 relative to K, maybe OTM.
S0_low = 50.0
K2 = 100.0
val2, boundary2, exercise2 = lattice.binomial_tree_value(
    n, S0_low, K2, T, r, sigma_spot, constant_sigma, sigma_offset)
print(f"S0={S0_low}, K={K2}")
print(f"Exercise at t=0? {exercise2[0]}")
print(f"Boundary[0] = {boundary2[0]}")
if boundary2[0] == np.inf:
    print("✅ No exercise at t=0 → boundary[0] = inf")
else:
    print(f"⚠️  Boundary[0] = {boundary2[0]} (expected inf)")

# Print a few more steps
for i in range(min(3, n+1)):
    dt = T / n
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    spots = S0_low * (u ** np.arange(i, -1, -1)) * (d ** np.arange(0, i+1))
    ex = exercise2[i]
    if np.any(ex):
        print(f"Step {i}: exercise True at spots {spots[ex].round(2)}")
        print(f"  Boundary[{i}] = {boundary2[i]:.2f} (smallest exercise spot = {np.min(spots[ex]):.2f})")
    else:
        print(f"Step {i}: no exercise, boundary[{i}] = {boundary2[i]}")

print("\n=== Conclusion ===")
print("The boundary array returns the smallest spot (lowest node) where exercise is optimal")
print("at each time step. For call spreads, this is the lower edge of the exercise region.")
print("At t=0, if exercise is True, boundary[0] = S0 (only spot); if exercise False, boundary[0] = inf.")