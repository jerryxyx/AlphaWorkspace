#!/usr/bin/env python3
"""
Debug premium values.
"""
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call, black_scholes_put
import numpy as np
from scipy.stats import norm

K = 200.0
sigma_fair = 0.8
sigma_offset = 0.3
sigma_spot = 0.9
T = 1.0
r = 0.10

def sigma_fair_func(spot):
    return sigma_fair

def unwind_call(spot, tau):
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    return black_scholes_call(spot, K, tau, r, vol_high) - black_scholes_call(spot, K, tau, r, vol_low)

def unwind_put(spot, tau):
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    return black_scholes_put(spot, K, tau, r, vol_high) - black_scholes_put(spot, K, tau, r, vol_low)

def continuation(spot, tau, option_type='call', n_small=10):
    if tau <= 0:
        return 0.0
    dt = tau / n_small
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    q = (np.exp(r * dt) - d) / (u - d)
    import lattice
    val_up, _, _ = lattice.binomial_tree_value(
        n_small - 1, spot * u, K, tau - dt, r, sigma_spot, sigma_fair_func,
        sigma_offset, option_type=option_type)
    val_down, _, _ = lattice.binomial_tree_value(
        n_small - 1, spot * d, K, tau - dt, r, sigma_spot, sigma_fair_func,
        sigma_offset, option_type=option_type)
    return np.exp(-r * dt) * (q * val_up + (1 - q) * val_down)

spots = [50, 100, 150, 200, 250, 300]
print("Spot | Unwind Call | Cont Call | Premium Call | Unwind Put | Cont Put | Premium Put")
print("-----|-------------|-----------|--------------|------------|----------|------------")
for s in spots:
    uc = unwind_call(s, T)
    cc = continuation(s, T, 'call', 10)
    pc = uc - cc
    up = unwind_put(s, T)
    cp = continuation(s, T, 'put', 10)
    pp = up - cp
    print(f"{s:4.0f} | {uc:11.6f} | {cc:9.6f} | {pc:12.6f} | {up:10.6f} | {cp:8.6f} | {pp:10.6f}")

print("\nCheck monotonicity:")
prem_c = [unwind_call(s, T) - continuation(s, T, 'call', 10) for s in spots]
prem_p = [unwind_put(s, T) - continuation(s, T, 'put', 10) for s in spots]
print("Call premium diff:", np.diff(prem_c))
print("Put premium diff:", np.diff(prem_p))