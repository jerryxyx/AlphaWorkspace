#!/usr/bin/env python3
"""
Test with small sigma_offset and large sigma_spot to see if waiting becomes optimal.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np

K = 100.0
S0 = 100.0
T = 1.0
r = 0.05
sigma_fair = 0.2
sigma_offset = 0.01   # small
sigma_spot = 0.5      # large

def sigma_fair_func(spot):
    return sigma_fair

# Compute American and European values
euro_call = lattice.black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(S0, K, T, r, sigma_fair)
amer_call, b_call, _ = lattice.binomial_tree_value(
    100, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
euro_put = lattice.black_scholes_put(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(S0, K, T, r, sigma_fair)
amer_put, b_put, _ = lattice.binomial_tree_value(
    100, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='put')

print(f"Parameters: σ_fair={sigma_fair}, σ_offset={sigma_offset}, σ_spot={sigma_spot}")
print(f"Call spread: European={euro_call:.6f}, American={amer_call:.6f}, premium={amer_call - euro_call:.6f}")
print(f"Put spread:  European={euro_put:.6f}, American={amer_put:.6f}, premium={amer_put - euro_put:.6f}")
print(f"Call boundary at t=0: {b_call[0]:.2f}, at t=T: {b_call[-1]:.2f}")
print(f"Put boundary at t=0: {b_put[0]:.2f}, at t=T: {b_put[-1]:.2f}")

# Compute premium across spots
spots = np.linspace(80, 120, 9)
print("\nSpot | Unwind Call | Cont Call | Premium Call | Exercise?")
print("-----|-------------|-----------|--------------|----------")
for s in spots:
    unwind = lattice.black_scholes_call(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
    # continuation using small tree
    dt = T / 20
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    q = (np.exp(r * dt) - d) / (u - d)
    val_up, _, _ = lattice.binomial_tree_value(
        19, s * u, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    val_down, _, _ = lattice.binomial_tree_value(
        19, s * d, K, T - dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    cont = np.exp(-r * dt) * (q * val_up + (1 - q) * val_down)
    prem = unwind - cont
    print(f"{s:4.0f} | {unwind:11.6f} | {cont:9.6f} | {prem:12.6f} | {unwind >= cont}")