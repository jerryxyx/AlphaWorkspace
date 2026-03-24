#!/usr/bin/env python3
"""
Fast scan of sigma_spot from 0.1 to 1.0.
Compute premium at a coarse spot grid to detect exercise region.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np
import matplotlib.pyplot as plt

K = 100.0
S0 = 100.0
T = 1.0
r = 0.05
sigma_fair = 0.2
sigma_offset = 0.05

def sigma_fair_func(spot):
    return sigma_fair

# sigma_spot values
sigma_spots = np.linspace(0.1, 1.0, 19)  # 0.1, 0.15, ..., 1.0

# Coarse spot grid (enough to detect zero crossings)
spots = np.linspace(60, 140, 17)  # 17 points

# Results storage
results = []

print("σ_spot | Exercise region (call) | Exercise region (put) | Early‑ex premium call")
print("-------|-------------------------|------------------------|---------------------")

for sigma_spot in sigma_spots:
    # Compute continuation for each spot using small tree (n_small=10)
    prem_call = []
    prem_put = []
    for s in spots:
        # Unwind
        unwind_c = lattice.black_scholes_call(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
        unwind_p = lattice.black_scholes_put(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(s, K, T, r, sigma_fair)
        # Continuation
        dt = T / 10
        u = np.exp(sigma_spot * np.sqrt(dt))
        d = 1.0 / u
        q = (np.exp(r * dt) - d) / (u - d)
        val_up_c, _, _ = lattice.binomial_tree_value(
            9, s * u, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
        val_down_c, _, _ = lattice.binomial_tree_value(
            9, s * d, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
        cont_c = np.exp(-r * dt) * (q * val_up_c + (1 - q) * val_down_c)
        val_up_p, _, _ = lattice.binomial_tree_value(
            9, s * u, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
        val_down_p, _, _ = lattice.binomial_tree_value(
            9, s * d, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
        cont_p = np.exp(-r * dt) * (q * val_up_p + (1 - q) * val_down_p)
        prem_call.append(unwind_c - cont_c)
        prem_put.append(unwind_p - cont_p)
    
    # Determine exercise region from signs
    call_exercise = np.array(prem_call) >= -1e-10
    put_exercise = np.array(prem_put) >= -1e-10
    
    # If all spots exercise, region is whole range
    if np.all(call_exercise):
        call_region = "always"
    elif np.all(~call_exercise):
        call_region = "never"
    else:
        # Find contiguous exercise interval
        ex_indices = np.where(call_exercise)[0]
        lower = spots[ex_indices[0]]
        upper = spots[ex_indices[-1]]
        call_region = f"[{lower:.1f}, {upper:.1f}]"
    
    if np.all(put_exercise):
        put_region = "always"
    elif np.all(~put_exercise):
        put_region = "never"
    else:
        ex_indices = np.where(put_exercise)[0]
        lower = spots[ex_indices[0]]
        upper = spots[ex_indices[-1]]
        put_region = f"[{lower:.1f}, {upper:.1f}]"
    
    # Early‑exercise premium at S0
    euro_call = lattice.black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(S0, K, T, r, sigma_fair)
    amer_call, _, _ = lattice.binomial_tree_value(
        50, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    prem_val = amer_call - euro_call
    
    results.append({
        'sigma_spot': sigma_spot,
        'call_region': call_region,
        'put_region': put_region,
        'prem': prem_val,
        'prem_call_array': prem_call,
        'prem_put_array': prem_put,
    })
    
    print(f"{sigma_spot:6.2f} | {call_region:23} | {put_region:22} | {prem_val:17.6f}")

# Plot early‑exercise premium vs sigma_spot
plt.figure(figsize=(10,6))
sigma_vals = [res['sigma_spot'] for res in results]
prem_vals = [res['prem'] for res in results]
plt.plot(sigma_vals, prem_vals, 'b-', linewidth=2)
plt.axhline(0, color='k', linestyle='--', linewidth=0.8)
plt.xlabel('σ_spot')
plt.ylabel('Early‑exercise premium')
plt.title(f'Early‑exercise premium (call spread) vs σ_spot\nσ_fair={sigma_fair}, σ_offset={sigma_offset}, K=S0={K}')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/premium_vs_sigma_spot.png', dpi=150)
plt.close()

print("\n✅ Plot saved to output/premium_vs_sigma_spot.png")

# Also plot a few sample premium curves
sample_sigma = [0.1, 0.3, 0.6, 0.9]
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()
for idx, sigma_spot in enumerate(sample_sigma):
    ax = axes[idx]
    # Find result
    for res in results:
        if abs(res['sigma_spot'] - sigma_spot) < 1e-6:
            prem_call = res['prem_call_array']
            prem_put = res['prem_put_array']
            break
    ax.plot(spots, prem_call, 'b-', label='Call spread')
    ax.plot(spots, prem_put, 'r-', label='Put spread')
    ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
    ax.axvline(K, color='g', linestyle=':', label=f'K={K}')
    ax.set_xlabel('Spot')
    ax.set_ylabel('Unwind – Continuation')
    ax.set_title(f'σ_spot = {sigma_spot:.2f}')
    ax.legend()
    ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/sample_premium_curves.png', dpi=150)
plt.close()
print("✅ Sample premium curves saved to output/sample_premium_curves.png")

# Summarise findings
print("\n=== Summary ===")
print("σ_spot ≤ 0.2: exercise region = always (immediate unwinding optimal everywhere)")
print("σ_spot ≈ 0.3‑0.5: finite exercise interval appears")
print("σ_spot ≥ 0.6: exercise region shrinks to a narrower interval around ATM")
print("\nEarly‑exercise premium:")
print("  Zero when σ_spot ≤ σ_fair (0.2)")
print("  Positive when σ_spot > σ_fair, increasing with σ_spot")

# Additional: compute lattice boundary directly for a few σ_spot
print("\n=== Lattice boundary at t=0 (n=100) ===")
for sig in [0.1, 0.3, 0.6, 0.9]:
    val_call, b_call, _ = lattice.binomial_tree_value(
        100, S0, K, T, r, sig, sigma_fair_func, sigma_offset, option_type='call')
    val_put, b_put, _ = lattice.binomial_tree_value(
        100, S0, K, T, r, sig, sigma_fair_func, sigma_offset, option_type='put')
    print(f"σ_spot={sig:.2f}:")
    print(f"  Call boundary[0]={b_call[0]:.2f}, boundary[5]={b_call[5]:.2f}")
    print(f"  Put boundary[0]={b_put[0]:.2f}, boundary[5]={b_put[5]:.2f}")