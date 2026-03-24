#!/usr/bin/env python3
"""
Plot finite exercise boundary scenario (small σ_offset, large σ_spot).
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
sigma_offset = 0.01   # small
sigma_spot = 0.5      # large

def sigma_fair_func(spot):
    return sigma_fair

def continuation(spot, tau, option_type='call', n_small=20):
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

spots = np.linspace(70, 130, 121)
prem_call = []
prem_put = []
for s in spots:
    unwind_c = lattice.black_scholes_call(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
    cont_c = continuation(s, T, 'call', 20)
    prem_call.append(unwind_c - cont_c)
    unwind_p = lattice.black_scholes_put(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(s, K, T, r, sigma_fair)
    cont_p = continuation(s, T, 'put', 20)
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

plt.figure(figsize=(10,6))
plt.plot(spots, prem_call, 'b-', label='Call spread premium')
plt.plot(spots, prem_put, 'r-', label='Put spread premium')
plt.axhline(0, color='k', linestyle='--', linewidth=0.8)
plt.axvline(K, color='g', linestyle=':', linewidth=1, label=f'K={K}')
for z in zeros_call:
    plt.axvline(z, color='b', linestyle='--', linewidth=0.8, alpha=0.7)
for z in zeros_put:
    plt.axvline(z, color='r', linestyle='--', linewidth=0.8, alpha=0.7)
plt.xlabel('Spot')
plt.ylabel('Unwind – Continuation')
plt.title(f'Finite exercise region: σ_fair={sigma_fair}, σ_offset={sigma_offset}, σ_spot={sigma_spot}')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/finite_boundary.png', dpi=150)
plt.close()

print("=== Finite boundary scenario ===")
print(f"σ_fair={sigma_fair}, σ_offset={sigma_offset}, σ_spot={sigma_spot}")
print(f"Call spread zero crossings: {zeros_call}")
print(f"Put spread zero crossings: {zeros_put}")
print("Exercise region (where premium ≥ 0):")
if len(zeros_call) == 2:
    print(f"  Call spread: spots between {zeros_call[0]:.2f} and {zeros_call[1]:.2f}")
elif len(zeros_call) == 1:
    print(f"  Call spread: spots {'above' if prem_call[-1] > 0 else 'below'} {zeros_call[0]:.2f}")
else:
    print("  Call spread: no finite boundary (premium never crosses zero).")
if len(zeros_put) == 2:
    print(f"  Put spread: spots between {zeros_put[0]:.2f} and {zeros_put[1]:.2f}")
elif len(zeros_put) == 1:
    print(f"  Put spread: spots {'above' if prem_put[-1] > 0 else 'below'} {zeros_put[0]:.2f}")
else:
    print("  Put spread: no finite boundary (premium never crosses zero).")

# Compute lattice boundary directly
n = 100
val_call, b_call, _ = lattice.binomial_tree_value(
    n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
val_put, b_put, _ = lattice.binomial_tree_value(
    n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')
print(f"\nLattice boundary (call) at t=0: {b_call[0]:.2f}")
print(f"Lattice boundary (put) at t=0: {b_put[0]:.2f}")
print("First few boundary steps (call):", b_call[:5])
print("First few boundary steps (put):", b_put[:5])

# Early‑exercise premium
euro_call = lattice.black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(S0, K, T, r, sigma_fair)
euro_put = lattice.black_scholes_put(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(S0, K, T, r, sigma_fair)
print(f"\nEuropean call spread: {euro_call:.6f}")
print(f"American call spread: {val_call:.6f}")
print(f"Early‑exercise premium: {val_call - euro_call:.6f}")
print(f"European put spread: {euro_put:.6f}")
print(f"American put spread: {val_put:.6f}")
print(f"Early‑exercise premium: {val_put - euro_put:.6f}")