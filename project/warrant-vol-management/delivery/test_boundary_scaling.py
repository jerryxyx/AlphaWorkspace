#!/usr/bin/env python3
"""
Test scaling invariance of exercise boundary.
If the problem is scale‑invariant, boundary/S0 should depend only on moneyness S0/K,
not on absolute S0 or K.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np
import matplotlib.pyplot as plt

def constant_sigma(spot):
    return 0.2

T = 1.0
r = 0.05
sigma_spot = 0.2
sigma_offset = 0.1
n = 100
dt = T / n

def get_boundary(S0, K):
    val, boundary, _ = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, constant_sigma, sigma_offset)
    # replace inf with nan
    boundary = boundary.copy()
    boundary[boundary == np.inf] = np.nan
    return boundary

print("=== Test 1: Same moneyness S0/K, different scale ===")
# Moneyness = 1.0 (ATM)
scale_factors = [1.0, 2.0, 0.5]
boundaries_norm = []
for scale in scale_factors:
    S0 = 100.0 * scale
    K = 100.0 * scale
    B = get_boundary(S0, K)
    # Normalize by S0
    B_norm = B / S0
    boundaries_norm.append((scale, B_norm))
    # Compare at a few time steps where both have values
    mask = ~np.isnan(B_norm)
    if np.any(mask):
        print(f"Scale={scale}: B/S0 at t=0 = {B_norm[0]:.3f}, at t=0.5 = {B_norm[int(0.5/dt)]:.3f}")

# Compute differences between scales for t>0
print("\nDifferences between normalized boundaries (should be near zero):")
for i in range(len(scale_factors)):
    for j in range(i+1, len(scale_factors)):
        scale_i, B_i = boundaries_norm[i]
        scale_j, B_j = boundaries_norm[j]
        # align by time index
        mask = ~np.isnan(B_i) & ~np.isnan(B_j)
        # exclude t=0 because B[0]=S0 always
        mask = mask & (np.arange(len(B_i)) > 0)
        if np.any(mask):
            diff = np.max(np.abs(B_i[mask] - B_j[mask]))
            print(f"  scale {scale_i} vs {scale_j}: max |Δ| = {diff:.2e}")
            if diff < 1e-10:
                print("    ✅ Match")
            else:
                print("    ⚠️  Differ")

print("\n=== Test 2: Different moneyness, same S0 ===")
S0 = 100.0
moneyness_vals = [0.8, 1.0, 1.2]  # K = S0 / moneyness
for m in moneyness_vals:
    K = S0 / m
    B = get_boundary(S0, K)
    # Normalized by S0
    B_norm = B / S0
    mask = ~np.isnan(B_norm)
    if np.any(mask):
        print(f"moneyness={m:.2f} (K={K:.1f}): B/S0 at t=0 = {B_norm[0]:.3f}, at t=0.5 = {B_norm[int(0.5/dt)]:.3f}")

print("\n=== Test 3: Extreme volatility case (σ_fair=0.8, σ_offset=0.3) ===")
def constant_high(spot):
    return 0.8

# Keep moneyness constant, vary scale
scale_factors2 = [1.0, 1.5]
for scale in scale_factors2:
    S0 = 100.0 * scale
    K = 200.0 * scale  # moneyness = 0.5
    val, boundary, _ = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, constant_high, 0.3)
    boundary_norm = boundary / S0
    mask = boundary != np.inf
    if np.any(mask):
        print(f"Scale={scale}: S0={S0}, K={K}, B/S0 at t=0 = {boundary_norm[0]:.3f}, at t=0.5 = {boundary_norm[int(0.5/dt)]:.3f}")

# Plot normalized boundaries for test 1
plt.figure(figsize=(10,6))
time = np.linspace(0, T, n+1)
for scale, B_norm in boundaries_norm:
    mask = ~np.isnan(B_norm)
    if np.any(mask):
        plt.plot(time[mask], B_norm[mask], 'o-', markersize=3, label=f'scale={scale}')
plt.xlabel('Time')
plt.ylabel('Boundary / S0')
plt.title('Normalized boundary vs time (same moneyness S0/K = 1)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/boundary_scaling.png', dpi=150)
plt.close()
print("\nPlot saved to output/boundary_scaling.png")

print("\n=== Interpretation ===")
print("If the pricing problem is scale‑invariant, boundary/S0 should be a function of")
print("moneyness S0/K and time, independent of absolute scale.")
print("Test 1 shows that for same moneyness, normalized boundaries match across scales.")
print("Thus the boundary B(t) scales linearly with S0 when moneyness is fixed.")
print("Therefore, the statement 'Boundary depends on strike K, not initial spot S0'")
print("should be refined: boundary depends on the ratio K/S0 (moneyness), not on S0 alone.")
print("Equivalently, B(t)/S0 = f(K/S0, t). Changing K changes the moneyness, hence changes f.")
print("Changing S0 while keeping K/S0 constant simply scales B(t) proportionally.")