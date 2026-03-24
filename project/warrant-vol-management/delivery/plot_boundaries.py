#!/usr/bin/env python3
"""
Plot exercise boundaries for ATM case across sigma_spot scenarios.
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
sigma_offset = 0.1

def sigma_fair_func(spot):
    return sigma_fair

scenarios = [
    ('σ_spot = 0.1 (< σ_fair)', 0.1),
    ('σ_spot = 0.2 (= σ_fair)', 0.2),
    ('σ_spot = 0.3 (> σ_fair)', 0.3),
]

n = 100
time_steps = np.linspace(0, T, n+1)

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
fig.suptitle('Exercise Boundaries for ATM Spreads (n=100)', fontsize=14)

for col, (label, sigma_spot) in enumerate(scenarios):
    # Call spread
    val_call, b_call, _ = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    ax = axes[0, col]
    ax.plot(time_steps, b_call, 'b-', linewidth=2)
    ax.axhline(K, color='g', linestyle=':', linewidth=1, label=f'K={K}')
    ax.set_xlabel('Time to expiry')
    ax.set_ylabel('Boundary spot')
    ax.set_title(f'Call spread – {label}')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Put spread
    val_put, b_put, _ = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
    ax = axes[1, col]
    ax.plot(time_steps, b_put, 'r-', linewidth=2)
    ax.axhline(K, color='g', linestyle=':', linewidth=1, label=f'K={K}')
    ax.set_xlabel('Time to expiry')
    ax.set_ylabel('Boundary spot')
    ax.set_title(f'Put spread – {label}')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    print(f"\n{label}:")
    print(f"  Call spread American value: {val_call:.6f}")
    print(f"  Put spread American value: {val_put:.6f}")
    print(f"  Call boundary at t=0: {b_call[0]:.2f}, at t=T: {b_call[-1]:.2f}")
    print(f"  Put boundary at t=0: {b_put[0]:.2f}, at t=T: {b_put[-1]:.2f}")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('output/atm_boundaries.png', dpi=150)
plt.close()

print("\n✅ Boundaries plotted to output/atm_boundaries.png")

# Also compute early‑exercise premium (American - European)
print("\n=== Early‑exercise premium ===")
for label, sigma_spot in scenarios:
    # European call spread value (no early exercise)
    euro_call = lattice.black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(S0, K, T, r, sigma_fair)
    # American from lattice
    amer_call, _, _ = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    prem_call = amer_call - euro_call
    # Put spread
    euro_put = lattice.black_scholes_put(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(S0, K, T, r, sigma_fair)
    amer_put, _, _ = lattice.binomial_tree_value(
        n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
    prem_put = amer_put - euro_put
    print(f"{label}:")
    print(f"  Call spread: European={euro_call:.6f}, American={amer_call:.6f}, premium={prem_call:.6f}")
    print(f"  Put spread:  European={euro_put:.6f}, American={amer_put:.6f}, premium={prem_put:.6f}")