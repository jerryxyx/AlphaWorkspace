#!/usr/bin/env python3
"""
Test ATM case (S₀ ≈ K) with sigma_spot less, equal, greater than sigma_fair.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np
import matplotlib.pyplot as plt

# Base parameters
K = 100.0
S0 = 100.0          # ATM
T = 1.0
r = 0.05
sigma_fair = 0.2
sigma_offset = 0.1   # high‑vol option = sigma_fair + offset

# Three scenarios
scenarios = [
    ('sigma_spot < sigma_fair', 0.1),
    ('sigma_spot = sigma_fair', 0.2),
    ('sigma_spot > sigma_fair', 0.3),
]

def sigma_fair_func(spot):
    return sigma_fair

def unwind_call(spot, tau):
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    return lattice.black_scholes_call(spot, K, tau, r, vol_high) - lattice.black_scholes_call(spot, K, tau, r, vol_low)

def unwind_put(spot, tau):
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    return lattice.black_scholes_put(spot, K, tau, r, vol_high) - lattice.black_scholes_put(spot, K, tau, r, vol_low)

def continuation(spot, tau, sigma_spot, option_type='call', n_small=20):
    """Continuation value using lattice with given sigma_spot."""
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

# Spot range
spots = np.linspace(50, 150, 101)

# Plot for each scenario
fig, axes = plt.subplots(3, 2, figsize=(14, 12))
fig.suptitle('ATM Case: Premium (unwind – continuation) at t=0', fontsize=14)

for row, (label, sigma_spot) in enumerate(scenarios):
    # Compute premiums
    prem_call = []
    prem_put = []
    for s in spots:
        uc = unwind_call(s, T)
        cc = continuation(s, T, sigma_spot, 'call', 10)
        prem_call.append(uc - cc)
        up = unwind_put(s, T)
        cp = continuation(s, T, sigma_spot, 'put', 10)
        prem_put.append(up - cp)
    
    # Call spread (left column)
    ax = axes[row, 0]
    ax.plot(spots, prem_call, 'b-', linewidth=2)
    ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
    ax.axvline(K, color='g', linestyle=':', linewidth=1, label=f'K={K}')
    ax.set_xlabel('Spot')
    ax.set_ylabel('Premium')
    ax.set_title(f'Call spread – {label}')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Find zero crossing for call spread
    def find_zero(x, y):
        for i in range(len(x)-1):
            if y[i] * y[i+1] <= 0:
                x0, x1 = x[i], x[i+1]
                y0, y1 = y[i], y[i+1]
                if abs(y1 - y0) < 1e-12:
                    return (x0 + x1) / 2
                return x0 - y0 * (x1 - x0) / (y1 - y0)
        return None
    zero_call = find_zero(spots, prem_call)
    if zero_call is not None:
        ax.axvline(zero_call, color='b', linestyle='--', linewidth=1, label=f'Boundary={zero_call:.2f}')
        ax.legend()
    
    # Put spread (right column)
    ax = axes[row, 1]
    ax.plot(spots, prem_put, 'r-', linewidth=2)
    ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
    ax.axvline(K, color='g', linestyle=':', linewidth=1, label=f'K={K}')
    ax.set_xlabel('Spot')
    ax.set_ylabel('Premium')
    ax.set_title(f'Put spread – {label}')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    zero_put = find_zero(spots, prem_put)
    if zero_put is not None:
        ax.axvline(zero_put, color='r', linestyle='--', linewidth=1, label=f'Boundary={zero_put:.2f}')
        ax.legend()
    
    # Print summary
    print(f"\n=== {label} (σ_spot={sigma_spot}) ===")
    print(f"Call spread premium range: {np.min(prem_call):.6f} .. {np.max(prem_call):.6f}")
    print(f"Put spread premium range: {np.min(prem_put):.6f} .. {np.max(prem_put):.6f}")
    if zero_call is not None:
        print(f"Call boundary spot: {zero_call:.2f}")
    else:
        print("Call boundary not found (premium never crosses zero).")
    if zero_put is not None:
        print(f"Put boundary spot: {zero_put:.2f}")
    else:
        print("Put boundary not found (premium never crosses zero).")
    
    # Monotonicity
    diff_call = np.diff(prem_call)
    diff_put = np.diff(prem_put)
    mono_call = np.all(diff_call >= -1e-10)
    mono_put = np.all(diff_put <= 1e-10)  # decreasing
    print(f"Call premium monotonic non‑decreasing? {mono_call}")
    print(f"Put premium monotonic non‑increasing? {mono_put}")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('output/atm_premiums.png', dpi=150)
plt.close()

print("\n✅ Plots saved to output/atm_premiums.png")

# Additional: compute lattice boundary directly for one scenario (σ_spot = σ_fair)
print("\n=== Direct lattice boundary (σ_spot = σ_fair) ===")
sigma_spot = 0.2
val_call, b_call, _ = lattice.binomial_tree_value(
    100, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
val_put, b_put, _ = lattice.binomial_tree_value(
    100, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
print(f"American call spread value: {val_call:.6f}")
print(f"American put spread value: {val_put:.6f}")
print(f"Boundary at t=0 (call): {b_call[0]:.2f}")
print(f"Boundary at t=0 (put): {b_put[0]:.2f}")
print(f"Boundary first few steps (call): {b_call[:5]}")
print(f"Boundary first few steps (put): {b_put[:5]}")