#!/usr/bin/env python3
"""
Vary sigma_spot from 0.1 to 1.0, fixed sigma_fair=0.2, sigma_offset=0.05, K=S0=100.
Check existence and range of exercise boundary.
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
print("σ_spot | Call boundary (lower) | Call boundary (upper) | Put boundary (lower) | Put boundary (upper) | Early‑exercise premium")
print("-------|------------------------|------------------------|----------------------|----------------------|----------------------")

# Store results
results = []

# Spot range for zero‑crossing detection
spots = np.linspace(50, 150, 201)

for sigma_spot in sigma_spots:
    # Compute continuation for each spot (call and put)
    prem_call = []
    prem_put = []
    for s in spots:
        # Unwind values
        unwind_c = lattice.black_scholes_call(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
        unwind_p = lattice.black_scholes_put(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(s, K, T, r, sigma_fair)
        # Continuation using small tree
        dt = T / 20
        u = np.exp(sigma_spot * np.sqrt(dt))
        d = 1.0 / u
        q = (np.exp(r * dt) - d) / (u - d)
        val_up_c, _, _ = lattice.binomial_tree_value(
            19, s * u, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
        val_down_c, _, _ = lattice.binomial_tree_value(
            19, s * d, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
        cont_c = np.exp(-r * dt) * (q * val_up_c + (1 - q) * val_down_c)
        val_up_p, _, _ = lattice.binomial_tree_value(
            19, s * u, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
        val_down_p, _, _ = lattice.binomial_tree_value(
            19, s * d, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
        cont_p = np.exp(-r * dt) * (q * val_up_p + (1 - q) * val_down_p)
        prem_call.append(unwind_c - cont_c)
        prem_put.append(unwind_p - cont_p)
    
    # Find zero crossings
    def find_zeros(x, y):
        zeros = []
        for i in range(len(x)-1):
            if y[i] * y[i+1] <= 0:
                x0, x1 = x[i], x[i+1]
                y0, y1 = y[i], y[i+1]
                if abs(y1 - y0) < 1e-12:
                    zero = (x0 + x1) / 2
                else:
                    zero = x0 - y0 * (x1 - x0) / (y1 - y0)
                zeros.append(zero)
        return zeros
    
    zeros_call = find_zeros(spots, prem_call)
    zeros_put = find_zeros(spots, prem_put)
    
    # Determine boundary range (call)
    if len(zeros_call) == 2:
        call_lower, call_upper = zeros_call[0], zeros_call[1]
    elif len(zeros_call) == 1:
        # Decide if exercise region is above or below
        if prem_call[-1] > 0:
            call_lower, call_upper = zeros_call[0], np.inf
        else:
            call_lower, call_upper = -np.inf, zeros_call[0]
    else:
        # No zero crossing: check if premium always positive or always negative
        if all(p > 0 for p in prem_call):
            call_lower, call_upper = -np.inf, np.inf  # always exercise
        else:
            call_lower, call_upper = np.nan, np.nan   # never exercise
    
    # Determine boundary range (put)
    if len(zeros_put) == 2:
        put_lower, put_upper = zeros_put[0], zeros_put[1]
    elif len(zeros_put) == 1:
        if prem_put[-1] > 0:
            put_lower, put_upper = zeros_put[0], np.inf
        else:
            put_lower, put_upper = -np.inf, zeros_put[0]
    else:
        if all(p > 0 for p in prem_put):
            put_lower, put_upper = -np.inf, np.inf
        else:
            put_lower, put_upper = np.nan, np.nan
    
    # Early‑exercise premium (American - European)
    euro_call = lattice.black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(S0, K, T, r, sigma_fair)
    amer_call, _, _ = lattice.binomial_tree_value(
        100, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    prem_call_val = amer_call - euro_call
    euro_put = lattice.black_scholes_put(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(S0, K, T, r, sigma_fair)
    amer_put, _, _ = lattice.binomial_tree_value(
        100, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
    prem_put_val = amer_put - euro_put
    
    # Store
    results.append({
        'sigma_spot': sigma_spot,
        'call_lower': call_lower,
        'call_upper': call_upper,
        'put_lower': put_lower,
        'put_upper': put_upper,
        'prem_call': prem_call_val,
        'prem_put': prem_put_val,
    })
    
    # Print
    print(f"{sigma_spot:6.2f} | {call_lower:20.2f} | {call_upper:20.2f} | {put_lower:20.2f} | {put_upper:20.2f} | {prem_call_val:18.6f}")

# Plot boundary ranges vs sigma_spot
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
# Call spread boundaries
ax = axes[0, 0]
sigma_vals = [r['sigma_spot'] for r in results]
call_lower = [r['call_lower'] for r in results]
call_upper = [r['call_upper'] for r in results]
ax.fill_between(sigma_vals, call_lower, call_upper, alpha=0.3, color='b', label='Exercise region')
ax.plot(sigma_vals, call_lower, 'b-', linewidth=1.5, label='Lower boundary')
ax.plot(sigma_vals, call_upper, 'b--', linewidth=1.5, label='Upper boundary')
ax.axhline(K, color='g', linestyle=':', label=f'K={K}')
ax.set_xlabel('σ_spot')
ax.set_ylabel('Spot')
ax.set_title('Call spread exercise region')
ax.legend()
ax.grid(True, alpha=0.3)

# Put spread boundaries
ax = axes[0, 1]
put_lower = [r['put_lower'] for r in results]
put_upper = [r['put_upper'] for r in results]
ax.fill_between(sigma_vals, put_lower, put_upper, alpha=0.3, color='r', label='Exercise region')
ax.plot(sigma_vals, put_lower, 'r-', linewidth=1.5, label='Lower boundary')
ax.plot(sigma_vals, put_upper, 'r--', linewidth=1.5, label='Upper boundary')
ax.axhline(K, color='g', linestyle=':', label=f'K={K}')
ax.set_xlabel('σ_spot')
ax.set_ylabel('Spot')
ax.set_title('Put spread exercise region')
ax.legend()
ax.grid(True, alpha=0.3)

# Early‑exercise premium (call)
ax = axes[1, 0]
prem_call = [r['prem_call'] for r in results]
ax.plot(sigma_vals, prem_call, 'b-', linewidth=2)
ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
ax.set_xlabel('σ_spot')
ax.set_ylabel('Premium')
ax.set_title('Call spread early‑exercise premium')
ax.grid(True, alpha=0.3)

# Early‑exercise premium (put)
ax = axes[1, 1]
prem_put = [r['prem_put'] for r in results]
ax.plot(sigma_vals, prem_put, 'r-', linewidth=2)
ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
ax.set_xlabel('σ_spot')
ax.set_ylabel('Premium')
ax.set_title('Put spread early‑exercise premium')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output/vary_sigma_spot.png', dpi=150)
plt.close()

print("\n✅ Plot saved to output/vary_sigma_spot.png")

# Summarise findings
print("\n=== Summary ===")
print("When σ_spot is low (≤ 0.2):")
for r in results[:3]:
    if r['call_lower'] == -np.inf and r['call_upper'] == np.inf:
        print(f"  σ_spot={r['sigma_spot']:.2f}: exercise region = entire spot range (always unwind)")
        break

print("\nWhen σ_spot is high (≥ 0.5):")
for r in results[-5:]:
    if not (np.isinf(r['call_lower']) and np.isinf(r['call_upper'])):
        print(f"  σ_spot={r['sigma_spot']:.2f}: finite exercise region [{r['call_lower']:.2f}, {r['call_upper']:.2f}]")
        break

# Print lattice boundary directly for a few σ_spot values
print("\n=== Direct lattice boundaries (n=100) ===")
for sigma_spot in [0.1, 0.3, 0.6, 0.9]:
    val_call, b_call, _ = lattice.binomial_tree_value(
        100, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    val_put, b_put, _ = lattice.binomial_tree_value(
        100, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
    print(f"σ_spot={sigma_spot:.2f}:")
    print(f"  Call boundary[0]={b_call[0]:.2f}, boundary[1]={b_call[1]:.2f}")
    print(f"  Put boundary[0]={b_put[0]:.2f}, boundary[1]={b_put[1]:.2f}")