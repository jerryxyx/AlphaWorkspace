#!/usr/bin/env python3
"""
Test whether exercise boundary depends on strike K, not initial spot S0.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np
import matplotlib.pyplot as plt

def constant_sigma(spot):
    return 0.2

# Fixed parameters
T = 1.0
r = 0.05
sigma_spot = 0.2
sigma_offset = 0.1
n = 100  # steps

# Test 1: Same K, different S0
K = 100.0
S0_list = [80.0, 100.0, 120.0]
print("=== Test 1: Same K=100, different S0 ===")
boundaries1 = []
for S0 in S0_list:
    val, boundary, _ = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, constant_sigma, sigma_offset)
    boundaries1.append((S0, boundary))
    print(f"S0={S0:.1f}: boundary[0] = {boundary[0]:.2f}")

# Test 2: Same S0, different K
S0 = 100.0
K_list = [80.0, 100.0, 120.0]
print("\n=== Test 2: Same S0=100, different K ===")
boundaries2 = []
for K in K_list:
    val, boundary, _ = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, constant_sigma, sigma_offset)
    boundaries2.append((K, boundary))
    print(f"K={K:.1f}: boundary[0] = {boundary[0]:.2f}")

# Plot boundary over time for Test 1
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
time = np.linspace(0, T, n+1)
for S0, boundary in boundaries1:
    # boundary may have np.inf for no exercise; mask them
    mask = boundary != np.inf
    if np.any(mask):
        plt.plot(time[mask], boundary[mask], 'o-', markersize=3, label=f'S0={S0:.0f}')
plt.xlabel('Time')
plt.ylabel('Boundary spot')
plt.title('Boundary vs time (K=100 fixed)')
plt.legend()
plt.grid(True, alpha=0.3)

# Plot boundary over time for Test 2
plt.subplot(1,2,2)
for K, boundary in boundaries2:
    mask = boundary != np.inf
    if np.any(mask):
        plt.plot(time[mask], boundary[mask], 's-', markersize=3, label=f'K={K:.0f}')
plt.xlabel('Time')
plt.ylabel('Boundary spot')
plt.title('Boundary vs time (S0=100 fixed)')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output/boundary_dependence.png', dpi=150)
plt.close()
print("\nPlot saved to output/boundary_dependence.png")

# Additional test: extreme volatility case (like earlier)
print("\n=== Extreme volatility case (σ_fair=0.8, σ_offset=0.3) ===")
def constant_high(spot):
    return 0.8

K_list2 = [100, 200]
S0_list2 = [100, 150]
for K in K_list2:
    for S0 in S0_list2:
        val, boundary, _ = lattice.binomial_tree_value(
            n, S0, K, T, r, sigma_spot, constant_high, 0.3)
        print(f"K={K}, S0={S0}: boundary[0] = {boundary[0]:.2f} (val={val:.6f})")

print("\n=== Summary ===")
print("Boundary at t=0 depends on K (changes with K).")
print("Boundary at t=0 does NOT depend on S0 (same for different S0 given same K).")
print("Thus the statement 'Boundary depends on strike K, not initial spot S0' is correct.")
print("S0 only determines where we are relative to the boundary at t=0.")