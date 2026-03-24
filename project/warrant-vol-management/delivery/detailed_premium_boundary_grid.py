#!/usr/bin/env python3
"""
Detailed premium and boundary analysis for call/put spreads.
Parameters:
  sigma_fair = 0.2
  S0 = K = 100.0
  T = 1.0
  r = 0.05
  sigma_spot from 0.20 to 0.30 step 0.01 (11 values)
  sigma_offset from 0.00 to 0.05 step 0.01 (6 values)
Compute premium across spots 50-150, determine exercise region boundaries.
Generate:
  1. Grid of premium curves (call left, put right) per (sigma_spot, sigma_offset)
  2. Heatmaps of lower/upper boundaries vs (sigma_spot, sigma_offset)
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

# Fixed parameters
sigma_fair = 0.2
K = 100.0
S0 = 100.0
T = 1.0
r = 0.05

# Parameter ranges
sigma_spot_vals = np.linspace(0.20, 0.30, 11)   # 0.20,0.21,...,0.30
sigma_offset_vals = np.linspace(0.00, 0.05, 6)   # 0.00,0.01,...,0.05
n_small = 5    # steps for continuation tree (smaller for speed)
spot_grid = np.linspace(50, 150, 21)   # coarse grid (21 points) for speed

def sigma_fair_func(spot):
    return sigma_fair

# Storage
results = []
premium_call = np.full((len(sigma_spot_vals), len(sigma_offset_vals), len(spot_grid)), np.nan)
premium_put = np.full((len(sigma_spot_vals), len(sigma_offset_vals), len(spot_grid)), np.nan)
boundary_call_lower = np.full((len(sigma_spot_vals), len(sigma_offset_vals)), np.nan)
boundary_call_upper = np.full((len(sigma_spot_vals), len(sigma_offset_vals)), np.nan)
boundary_put_lower = np.full((len(sigma_spot_vals), len(sigma_offset_vals)), np.nan)
boundary_put_upper = np.full((len(sigma_spot_vals), len(sigma_offset_vals)), np.nan)

print("Computing premiums and boundaries...")
total = len(sigma_spot_vals) * len(sigma_offset_vals)
count = 0

for i, sigma_spot in enumerate(sigma_spot_vals):
    for j, sigma_offset in enumerate(sigma_offset_vals):
        count += 1
        if count % 10 == 0:
            print(f"  {count}/{total}")
        
        # Precompute continuation parameters (same for all spots)
        dt = T / n_small
        u = np.exp(sigma_spot * np.sqrt(dt))
        d = 1.0 / u
        q = (np.exp(r * dt) - d) / (u - d)
        
        # Loop over spots
        prem_c = []
        prem_p = []
        for s in spot_grid:
            # Unwind values
            unwind_c = lattice.black_scholes_call(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
            unwind_p = lattice.black_scholes_put(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(s, K, T, r, sigma_fair)
            # Continuation values
            val_up_c, _, _ = lattice.binomial_tree_value(
                n_small - 1, s * u, K, T - dt, r, sigma_spot, sigma_fair_func,
                sigma_offset, option_type='call')
            val_down_c, _, _ = lattice.binomial_tree_value(
                n_small - 1, s * d, K, T - dt, r, sigma_spot, sigma_fair_func,
                sigma_offset, option_type='call')
            cont_c = np.exp(-r * dt) * (q * val_up_c + (1 - q) * val_down_c)
            val_up_p, _, _ = lattice.binomial_tree_value(
                n_small - 1, s * u, K, T - dt, r, sigma_spot, sigma_fair_func,
                sigma_offset, option_type='put')
            val_down_p, _, _ = lattice.binomial_tree_value(
                n_small - 1, s * d, K, T - dt, r, sigma_spot, sigma_fair_func,
                sigma_offset, option_type='put')
            cont_p = np.exp(-r * dt) * (q * val_up_p + (1 - q) * val_down_p)
            prem_c.append(unwind_c - cont_c)
            prem_p.append(unwind_p - cont_p)
        
        premium_call[i, j] = prem_c
        premium_put[i, j] = prem_p
        
        # Determine zero crossings for call spread
        zeros_c = []
        for k in range(len(spot_grid)-1):
            if prem_c[k] * prem_c[k+1] <= 0:
                x0, x1 = spot_grid[k], spot_grid[k+1]
                y0, y1 = prem_c[k], prem_c[k+1]
                if abs(y1 - y0) < 1e-12:
                    zero = (x0 + x1) / 2
                else:
                    zero = x0 - y0 * (x1 - x0) / (y1 - y0)
                zeros_c.append(zero)
        # For call spread, exercise region is where premium >= 0.
        # Typically premium positive for high spots -> lower boundary.
        # If two zeros, maybe finite range.
        if len(zeros_c) == 0:
            if all(p >= 0 for p in prem_c):
                # always exercise
                boundary_call_lower[i, j] = -np.inf
                boundary_call_upper[i, j] = np.inf
            else:
                # never exercise
                boundary_call_lower[i, j] = np.nan
                boundary_call_upper[i, j] = np.nan
        elif len(zeros_c) == 1:
            z = zeros_c[0]
            # Determine which side is exercise
            idx = np.where(spot_grid > z)[0][0]
            if prem_c[idx] >= 0:
                # exercise above z
                boundary_call_lower[i, j] = z
                boundary_call_upper[i, j] = np.inf
            else:
                boundary_call_lower[i, j] = -np.inf
                boundary_call_upper[i, j] = z
        else:
            # two or more zeros: assume finite range between first and last zero
            zeros_c.sort()
            boundary_call_lower[i, j] = zeros_c[0]
            boundary_call_upper[i, j] = zeros_c[-1]
        
        # Determine zero crossings for put spread
        zeros_p = []
        for k in range(len(spot_grid)-1):
            if prem_p[k] * prem_p[k+1] <= 0:
                x0, x1 = spot_grid[k], spot_grid[k+1]
                y0, y1 = prem_p[k], prem_p[k+1]
                if abs(y1 - y0) < 1e-12:
                    zero = (x0 + x1) / 2
                else:
                    zero = x0 - y0 * (x1 - x0) / (y1 - y0)
                zeros_p.append(zero)
        if len(zeros_p) == 0:
            if all(p >= 0 for p in prem_p):
                boundary_put_lower[i, j] = -np.inf
                boundary_put_upper[i, j] = np.inf
            else:
                boundary_put_lower[i, j] = np.nan
                boundary_put_upper[i, j] = np.nan
        elif len(zeros_p) == 1:
            z = zeros_p[0]
            idx = np.where(spot_grid > z)[0][0]
            if prem_p[idx] >= 0:
                # exercise above z
                boundary_put_lower[i, j] = z
                boundary_put_upper[i, j] = np.inf
            else:
                boundary_put_lower[i, j] = -np.inf
                boundary_put_upper[i, j] = z
        else:
            zeros_p.sort()
            boundary_put_lower[i, j] = zeros_p[0]
            boundary_put_upper[i, j] = zeros_p[-1]
        
        # Store results
        results.append({
            'sigma_spot': sigma_spot,
            'sigma_offset': sigma_offset,
            'call_lower': boundary_call_lower[i, j],
            'call_upper': boundary_call_upper[i, j],
            'put_lower': boundary_put_lower[i, j],
            'put_upper': boundary_put_upper[i, j],
        })

# Save results to CSV
df = pd.DataFrame(results)
csv_path = 'output/detailed_boundaries.csv'
df.to_csv(csv_path, index=False)
print(f"\n✅ Detailed boundaries saved to {csv_path}")

# 1. Grid of premium curves (call left, put right) per (sigma_spot, sigma_offset)
# We'll create a figure with rows = sigma_spot, columns = sigma_offset, each cell has two small plots.
# That's 11 rows × 6 columns = 66 cells, each cell with two tiny plots. Might be too crowded.
# Instead, we can create separate figures for call and put, each with subplots for sigma_offset lines per sigma_spot.
# Let's produce two figures: one for call spreads, one for put spreads, each with rows = sigma_spot, columns = sigma_offset (lines across spots).
# Actually we can do: for each sigma_spot, one subplot with multiple sigma_offset lines (call), another subplot for put.
# That's 11 rows × 2 columns = 22 subplots. Manageable.
fig, axes = plt.subplots(11, 2, figsize=(12, 30))
fig.suptitle('Premium (unwind – continuation) for σ_fair=0.2, S₀=K=100', fontsize=16)
for row, sigma_spot in enumerate(sigma_spot_vals):
    ax_c = axes[row, 0]
    ax_p = axes[row, 1]
    for j, sigma_offset in enumerate(sigma_offset_vals):
        color = cm.viridis(j / (len(sigma_offset_vals)-1))
        ax_c.plot(spot_grid, premium_call[row, j], color=color, linewidth=1.5, alpha=0.7,
                  label=f'σ_offset={sigma_offset:.2f}' if row==0 else None)
        ax_p.plot(spot_grid, premium_put[row, j], color=color, linewidth=1.5, alpha=0.7,
                  label=f'σ_offset={sigma_offset:.2f}' if row==0 else None)
    ax_c.axhline(0, color='k', linestyle='--', linewidth=0.8)
    ax_c.axvline(K, color='g', linestyle=':', linewidth=1, label='K')
    ax_c.set_xlabel('Spot')
    ax_c.set_ylabel('Premium')
    ax_c.set_title(f'Call spread, σ_spot={sigma_spot:.2f}')
    ax_c.grid(True, alpha=0.3)
    if row == 0:
        ax_c.legend(loc='upper left', fontsize='small')
    
    ax_p.axhline(0, color='k', linestyle='--', linewidth=0.8)
    ax_p.axvline(K, color='g', linestyle=':', linewidth=1, label='K')
    ax_p.set_xlabel('Spot')
    ax_p.set_ylabel('Premium')
    ax_p.set_title(f'Put spread, σ_spot={sigma_spot:.2f}')
    ax_p.grid(True, alpha=0.3)
    if row == 0:
        ax_p.legend(loc='upper left', fontsize='small')

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig('output/premium_grid_call_put.png', dpi=150)
plt.close()

# 2. Heatmaps of boundaries
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
# Call lower boundary
ax = axes[0, 0]
im = ax.imshow(boundary_call_lower.T, aspect='auto', origin='lower',
               extent=[sigma_spot_vals[0], sigma_spot_vals[-1],
                       sigma_offset_vals[0], sigma_offset_vals[-1]],
               cmap='viridis')
ax.set_xlabel('σ_spot')
ax.set_ylabel('σ_offset')
ax.set_title('Call spread lower boundary (exercise above)')
plt.colorbar(im, ax=ax)
# Call upper boundary
ax = axes[0, 1]
im = ax.imshow(boundary_call_upper.T, aspect='auto', origin='lower',
               extent=[sigma_spot_vals[0], sigma_spot_vals[-1],
                       sigma_offset_vals[0], sigma_offset_vals[-1]],
               cmap='viridis')
ax.set_xlabel('σ_spot')
ax.set_ylabel('σ_offset')
ax.set_title('Call spread upper boundary (exercise below)')
plt.colorbar(im, ax=ax)
# Put lower boundary
ax = axes[1, 0]
im = ax.imshow(boundary_put_lower.T, aspect='auto', origin='lower',
               extent=[sigma_spot_vals[0], sigma_spot_vals[-1],
                       sigma_offset_vals[0], sigma_offset_vals[-1]],
               cmap='viridis')
ax.set_xlabel('σ_spot')
ax.set_ylabel('σ_offset')
ax.set_title('Put spread lower boundary (exercise above)')
plt.colorbar(im, ax=ax)
# Put upper boundary
ax = axes[1, 1]
im = ax.imshow(boundary_put_upper.T, aspect='auto', origin='lower',
               extent=[sigma_spot_vals[0], sigma_spot_vals[-1],
                       sigma_offset_vals[0], sigma_offset_vals[-1]],
               cmap='viridis')
ax.set_xlabel('σ_spot')
ax.set_ylabel('σ_offset')
ax.set_title('Put spread upper boundary (exercise below)')
plt.colorbar(im, ax=ax)

plt.tight_layout()
plt.savefig('output/boundary_heatmaps.png', dpi=150)
plt.close()

print("✅ Generated plots:")
print("  - premium_grid_call_put.png (11 rows, 2 columns)")
print("  - boundary_heatmaps.png (2x2 heatmaps)")

# Also create a combined boundary plot similar to vary_sigma_spot.png but for call and put separately
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
# Call spread exercise region (shade between lower and upper)
ax = axes[0]
for j, sigma_offset in enumerate(sigma_offset_vals):
    color = cm.viridis(j / (len(sigma_offset_vals)-1))
    ax.fill_between(sigma_spot_vals,
                    boundary_call_lower[:, j],
                    boundary_call_upper[:, j],
                    alpha=0.3, color=color, label=f'σ_offset={sigma_offset:.2f}')
ax.set_xlabel('σ_spot')
ax.set_ylabel('Spot')
ax.set_title('Call spread exercise region (shaded)')
ax.legend()
ax.grid(True, alpha=0.3)
# Put spread exercise region
ax = axes[1]
for j, sigma_offset in enumerate(sigma_offset_vals):
    color = cm.viridis(j / (len(sigma_offset_vals)-1))
    ax.fill_between(sigma_spot_vals,
                    boundary_put_lower[:, j],
                    boundary_put_upper[:, j],
                    alpha=0.3, color=color, label=f'σ_offset={sigma_offset:.2f}')
ax.set_xlabel('σ_spot')
ax.set_ylabel('Spot')
ax.set_title('Put spread exercise region (shaded)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/exercise_regions_shaded.png', dpi=150)
plt.close()
print("  - exercise_regions_shaded.png")

print("\n=== Summary of boundary ranges ===")
print("For each σ_spot, exercise region (spot range where premium ≥ 0):")
for i, sigma_spot in enumerate(sigma_spot_vals):
    print(f"\nσ_spot = {sigma_spot:.2f}:")
    for j, sigma_offset in enumerate(sigma_offset_vals):
        cl = boundary_call_lower[i, j]
        cu = boundary_call_upper[i, j]
        pl = boundary_put_lower[i, j]
        pu = boundary_put_upper[i, j]
        print(f"  σ_offset={sigma_offset:.2f}: call [{cl:.1f},{cu:.1f}], put [{pl:.1f},{pu:.1f}]")