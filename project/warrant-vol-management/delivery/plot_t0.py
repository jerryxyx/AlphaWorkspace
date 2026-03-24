#!/usr/bin/env python3
"""
Plot premium at t=0 for call and put spreads across wide spot range.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np
import matplotlib.pyplot as plt

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
    return lattice.black_scholes_call(spot, K, tau, r, vol_high) - lattice.black_scholes_call(spot, K, tau, r, vol_low)

def unwind_put(spot, tau):
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    return lattice.black_scholes_put(spot, K, tau, r, vol_high) - lattice.black_scholes_put(spot, K, tau, r, vol_low)

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

spots = np.linspace(1, 400, 200)
prem_call = []
prem_put = []
for s in spots:
    uc = unwind_call(s, T)
    cc = continuation(s, T, 'call', 10)
    prem_call.append(uc - cc)
    up = unwind_put(s, T)
    cp = continuation(s, T, 'put', 10)
    prem_put.append(up - cp)

plt.figure(figsize=(10,6))
plt.plot(spots, prem_call, 'b-', label='Call spread premium')
plt.plot(spots, prem_put, 'r-', label='Put spread premium')
plt.axhline(0, color='k', linestyle='--', linewidth=0.8)
plt.axvline(K, color='g', linestyle=':', label=f'K={K}')
plt.xlabel('Spot')
plt.ylabel('Unwind - Continuation')
plt.title('Premium at t=0 (unwind - continuation)')
plt.legend()
plt.grid(True, alpha=0.3)

# Find zero crossings
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
zero_put = find_zero(spots, prem_put)
if zero_call is not None:
    plt.axvline(zero_call, color='b', linestyle='--', linewidth=0.8, label=f'Call boundary={zero_call:.1f}')
if zero_put is not None:
    plt.axvline(zero_put, color='r', linestyle='--', linewidth=0.8, label=f'Put boundary={zero_put:.1f}')

plt.tight_layout()
plt.savefig('output/premium_t0.png', dpi=150)
plt.close()

print("=== Results at t=0 ===")
print(f"Call spread premium positive for all spots? {all(p > 0 for p in prem_call)}")
print(f"Put spread premium positive for all spots? {all(p > 0 for p in prem_put)}")
if zero_call is not None:
    print(f"Call boundary spot: {zero_call:.2f}")
else:
    print("Call boundary not found in range (premium > 0 everywhere).")
if zero_put is not None:
    print(f"Put boundary spot: {zero_put:.2f}")
else:
    print("Put boundary not found in range (premium > 0 everywhere).")

# Compute monotonicity
diff_call = np.diff(prem_call)
diff_put = np.diff(prem_put)
mono_call = np.all(diff_call >= -1e-10)
mono_put = np.all(diff_put <= 1e-10)  # decreasing
print(f"\nMonotonicity:")
print(f"Call spread premium monotonic non‑decreasing? {mono_call}")
print(f"Put spread premium monotonic non‑increasing? {mono_put}")
if not mono_call:
    print("Call premium changes sign in diff:", diff_call[:10])
if not mono_put:
    print("Put premium changes sign in diff:", diff_put[:10])