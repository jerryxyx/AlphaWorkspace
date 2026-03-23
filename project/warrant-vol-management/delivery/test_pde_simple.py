#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
import numpy as np
import pde

# Simple test with constant volatility
S_min = 1.0
S_max = 300.0
n_S = 50  # small grid for speed
n_t = 50
S0 = 100.0
K = 100.0
T = 1.0
r = 0.05
sigma_spot = 0.2
sigma_fair_func = lambda s: 0.2
sigma_offset = 0.1

print("Testing PDE solver...")
val, V_history, boundary = pde.pde_value(
    S_min, S_max, n_S, n_t, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset,
    method='implicit'
)
print(f"PDE value: {val}")
print(f"Boundary (first 5): {boundary[:5]}")
print(f"Boundary finite: {boundary[np.isfinite(boundary)]}")

# Compare with European difference
from pde import black_scholes_call
vol_low = sigma_fair_func(S0)
vol_high = vol_low + sigma_offset
price_low = black_scholes_call(S0, K, T, r, vol_low)
price_high = black_scholes_call(S0, K, T, r, vol_high)
european_diff = price_high - price_low
print(f"European diff: {european_diff}")
print(f"Early exercise premium: {val - european_diff}")

# Plot if possible
try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10,6))
    # Plot value profile at time 0
    S_grid = np.linspace(S_min, S_max, n_S)
    plt.plot(S_grid, V_history[:, 0], label='V(S,0)')
    # Plot exercise value at time 0
    unwind = np.zeros_like(S_grid)
    for i, S in enumerate(S_grid):
        vol_low = sigma_fair_func(S)
        vol_high = vol_low + sigma_offset
        price_low = black_scholes_call(S, K, T, r, vol_low)
        price_high = black_scholes_call(S, K, T, r, vol_high)
        unwind[i] = price_high - price_low
    plt.plot(S_grid, unwind, '--', label='Unwind value')
    plt.axvline(S0, color='r', linestyle=':', label=f'S0={S0}')
    plt.xlabel('Spot')
    plt.ylabel('Value')
    plt.title('PDE Solution at t=0')
    plt.legend()
    plt.grid(True)
    plt.savefig('output/pde_test.png', dpi=150)
    plt.close()
    print("Plot saved to output/pde_test.png")
except:
    pass