#!/usr/bin/env python3
"""
Compute exercise boundary as function of time to maturity for varying sigma_fair and sigma_offset.
Assume sigma_spot = sigma_fair.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

K = 100.0
S0 = 100.0
T = 1.0
r = 0.05
# sigma_spot = sigma_fair (for each run)
n = 100   # time steps

# Parameter ranges
sigma_fair_vals = np.linspace(0.2, 0.4, 21)   # 0.20, 0.21, ..., 0.40
sigma_offset_vals = np.linspace(0.0, 0.1, 11)  # 0.00, 0.01, ..., 0.10

# Storage: boundaries[sigma_fair_idx][sigma_offset_idx] = boundary array (n+1)
boundaries = np.full((len(sigma_fair_vals), len(sigma_offset_vals), n+1), np.nan)
# Also store initial value (American spread price)
values = np.full((len(sigma_fair_vals), len(sigma_offset_vals)), np.nan)

print("Computing boundaries for", len(sigma_fair_vals)*len(sigma_offset_vals), "combinations...")

for i, sigma_fair in enumerate(sigma_fair_vals):
    sigma_spot = sigma_fair  # assume spot volatility equals fair implied vol
    def sigma_fair_func(spot):
        return sigma_fair
    for j, sigma_offset in enumerate(sigma_offset_vals):
        # Compute lattice for call spread
        val, boundary, _ = lattice.binomial_tree_value(
            n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
        boundaries[i, j] = boundary
        values[i, j] = val
        # Print progress
        if (i*len(sigma_offset_vals) + j) % 20 == 0:
            print(f"  σ_fair={sigma_fair:.2f}, σ_offset={sigma_offset:.2f}: val={val:.4f}, boundary[0]={boundary[0]:.2f}")

print("Done.")

# Time to expiry array (tau)
tau = np.linspace(T, 0, n+1)  # decreasing from T to 0

# 1. Heatmap of boundary at t=0 (initial boundary) vs (σ_fair, σ_offset)
boundary_t0 = boundaries[:, :, 0]  # shape (21,11)
plt.figure(figsize=(10,8))
plt.imshow(boundary_t0.T, aspect='auto', origin='lower',
           extent=[sigma_fair_vals[0], sigma_fair_vals[-1],
                   sigma_offset_vals[0], sigma_offset_vals[-1]],
           cmap='viridis')
plt.colorbar(label='Boundary spot at t=0')
plt.xlabel('σ_fair')
plt.ylabel('σ_offset')
plt.title('Exercise boundary at t=0 (call spread, S₀=K=100)')
plt.grid(False)
plt.tight_layout()
plt.savefig('output/boundary_t0_heatmap.png', dpi=150)
plt.close()

# 2. Heatmap of boundary at tau = T/2 (mid‑life)
mid_idx = n // 2
boundary_mid = boundaries[:, :, mid_idx]
plt.figure(figsize=(10,8))
plt.imshow(boundary_mid.T, aspect='auto', origin='lower',
           extent=[sigma_fair_vals[0], sigma_fair_vals[-1],
                   sigma_offset_vals[0], sigma_offset_vals[-1]],
           cmap='viridis')
plt.colorbar(label=f'Boundary spot at τ={tau[mid_idx]:.2f}')
plt.xlabel('σ_fair')
plt.ylabel('σ_offset')
plt.title(f'Exercise boundary at τ={tau[mid_idx]:.2f} (call spread, S₀=K=100)')
plt.grid(False)
plt.tight_layout()
plt.savefig('output/boundary_mid_heatmap.png', dpi=150)
plt.close()

# 3. Heatmap of American spread value at t=0
plt.figure(figsize=(10,8))
plt.imshow(values.T, aspect='auto', origin='lower',
           extent=[sigma_fair_vals[0], sigma_fair_vals[-1],
                   sigma_offset_vals[0], sigma_offset_vals[-1]],
           cmap='plasma')
plt.colorbar(label='American spread value')
plt.xlabel('σ_fair')
plt.ylabel('σ_offset')
plt.title('American call‑spread value at t=0 (S₀=K=100)')
plt.grid(False)
plt.tight_layout()
plt.savefig('output/spread_value_heatmap.png', dpi=150)
plt.close()

# 4. Selected boundary curves for a few combinations
selected_fair = [0.2, 0.3, 0.4]
selected_offset = [0.0, 0.05, 0.1]
fig, axes = plt.subplots(3, 3, figsize=(14, 12), sharex=True, sharey=True)
fig.suptitle('Exercise boundary vs time to expiry (call spread, S₀=K=100)', fontsize=14)
for row, sigma_offset in enumerate(selected_offset):
    for col, sigma_fair in enumerate(selected_fair):
        ax = axes[row, col]
        i = np.where(np.abs(sigma_fair_vals - sigma_fair) < 1e-6)[0][0]
        j = np.where(np.abs(sigma_offset_vals - sigma_offset) < 1e-6)[0][0]
        boundary = boundaries[i, j]
        ax.plot(tau, boundary, 'b-', linewidth=2)
        ax.axhline(K, color='g', linestyle=':', linewidth=1, label=f'K={K}')
        ax.set_xlabel('Time to expiry τ')
        ax.set_ylabel('Boundary spot')
        ax.set_title(f'σ_fair={sigma_fair:.2f}, σ_offset={sigma_offset:.2f}')
        ax.grid(True, alpha=0.3)
        ax.legend()
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('output/selected_boundary_curves.png', dpi=150)
plt.close()

# 5. 3D surface of boundary at t=0
fig = plt.figure(figsize=(12,10))
ax = fig.add_subplot(111, projection='3d')
X, Y = np.meshgrid(sigma_fair_vals, sigma_offset_vals, indexing='ij')
surf = ax.plot_surface(X, Y, boundary_t0, cmap='viridis', edgecolor='none')
ax.set_xlabel('σ_fair')
ax.set_ylabel('σ_offset')
ax.set_zlabel('Boundary spot at t=0')
ax.set_title('Exercise boundary at t=0 (call spread)')
fig.colorbar(surf, shrink=0.5, aspect=10)
plt.tight_layout()
plt.savefig('output/boundary_3d.png', dpi=150)
plt.close()

print("\n✅ Plots saved:")
print("  - boundary_t0_heatmap.png")
print("  - boundary_mid_heatmap.png")
print("  - spread_value_heatmap.png")
print("  - selected_boundary_curves.png")
print("  - boundary_3d.png")

# Additional: print summary table for some combos
print("\n=== Summary for selected combos ===")
print("σ_fair | σ_offset | Boundary[0] | Boundary[mid] | American value")
print("-------|----------|-------------|---------------|----------------")
for sigma_fair in selected_fair:
    for sigma_offset in selected_offset:
        i = np.where(np.abs(sigma_fair_vals - sigma_fair) < 1e-6)[0][0]
        j = np.where(np.abs(sigma_offset_vals - sigma_offset) < 1e-6)[0][0]
        b0 = boundaries[i, j, 0]
        bmid = boundaries[i, j, mid_idx]
        val = values[i, j]
        print(f"{sigma_fair:6.2f} | {sigma_offset:8.2f} | {b0:11.2f} | {bmid:13.2f} | {val:14.4f}")