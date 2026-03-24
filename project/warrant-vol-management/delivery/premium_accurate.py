#!/usr/bin/env python3
"""
Compute accurate unwind premium (unwind - continuation) using a small lattice.
"""
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Parameters
K = 200.0
S0 = 100.0
sigma_fair = 0.8
sigma_offset = 0.3
sigma_spot = 0.9
T = 1.0
r = 0.10

def sigma_fair_func(spot):
    return sigma_fair

def unwind_call_spread(spot, time_to_expiry):
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    C_high = black_scholes_call(spot, K, time_to_expiry, r, vol_high)
    C_low = black_scholes_call(spot, K, time_to_expiry, r, vol_low)
    return C_high - C_low

def unwind_put_spread(spot, time_to_expiry):
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    P_high = black_scholes_put(spot, K, time_to_expiry, r, vol_high)
    P_low = black_scholes_put(spot, K, time_to_expiry, r, vol_low)
    return P_high - P_low

def black_scholes_put(spot, strike, time_to_expiry, risk_free_rate, volatility):
    """European put price via Black-Scholes formula."""
    if time_to_expiry <= 0.0:
        return max(strike - spot, 0.0)
    d1 = (np.log(spot / strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) \
         / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)
    return strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - spot * norm.cdf(-d1)

def continuation_value(spot, time_to_expiry, option_type='call', n_small=20):
    """
    Compute continuation value using a small binomial tree with n_small steps.
    Returns discounted expectation of option values after dt.
    """
    if time_to_expiry <= 0.0:
        return 0.0
    tau = time_to_expiry
    dt = tau / n_small
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    q = (np.exp(r * dt) - d) / (u - d)
    
    # Spots after one step
    spot_up = spot * u
    spot_down = spot * d
    
    # American values at t+dt using lattice with appropriate option_type
    import lattice
    val_up, _, _ = lattice.binomial_tree_value(
        n_small - 1, spot_up, K, tau - dt, r, sigma_spot, sigma_fair_func,
        sigma_offset, option_type=option_type)
    val_down, _, _ = lattice.binomial_tree_value(
        n_small - 1, spot_down, K, tau - dt, r, sigma_spot, sigma_fair_func,
        sigma_offset, option_type=option_type)
    
    # Continuation = discounted expectation
    continuation = np.exp(-r * dt) * (q * val_up + (1 - q) * val_down)
    return continuation

# Spot range
spots = np.linspace(50, 300, 51)  # coarse for speed
times = [0.0, 0.25, 0.5, 0.75]

# Compute premiums
premiums_call = []
premiums_put = []
for t in times:
    prem_call = []
    prem_put = []
    for s in spots:
        unwind_c = unwind_call_spread(s, T - t)
        cont_c = continuation_value(s, T - t, option_type='call', n_small=10)
        prem_call.append(unwind_c - cont_c)
        
        unwind_p = unwind_put_spread(s, T - t)
        cont_p = continuation_value(s, T - t, option_type='put', n_small=10)
        prem_put.append(unwind_p - cont_p)
    premiums_call.append(prem_call)
    premiums_put.append(prem_put)

# Plot
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()
for idx, t in enumerate(times):
    ax = axes[idx]
    ax.plot(spots, premiums_call[idx], 'b-', label='Call spread premium')
    ax.plot(spots, premiums_put[idx], 'r-', label='Put spread premium')
    ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
    ax.axvline(K, color='g', linestyle=':', label=f'K={K}')
    ax.set_xlabel('Spot')
    ax.set_ylabel('Unwind - Continuation')
    ax.set_title(f't = {t:.2f}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
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
    zero_call = find_zero(spots, premiums_call[idx])
    zero_put = find_zero(spots, premiums_put[idx])
    if zero_call is not None:
        ax.axvline(zero_call, color='b', linestyle='--', linewidth=0.8, label=f'Call boundary={zero_call:.1f}')
    if zero_put is not None:
        ax.axvline(zero_put, color='r', linestyle='--', linewidth=0.8, label=f'Put boundary={zero_put:.1f}')

plt.tight_layout()
plt.savefig('output/premium_accurate.png', dpi=150)
plt.close()

print("=== Summary ===")
print("Plots saved to output/premium_accurate.png")
print("Zero crossing indicates exercise boundary:")
print("  Call spread: lowest spot where premium ≥ 0 (exercise above)")
print("  Put spread: highest spot where premium ≥ 0 (exercise below)")

# Monotonicity check at t=0
print("\n=== Monotonicity at t=0 ===")
prem_call_t0 = premiums_call[0]
prem_put_t0 = premiums_put[0]
diff_call = np.diff(prem_call_t0)
diff_put = np.diff(prem_put_t0)
if np.all(diff_call >= -1e-10):
    print("Call spread premium monotonic non‑decreasing.")
else:
    print("Call spread premium NOT monotonic.")
    print("Differences:", diff_call[:5])
if np.all(diff_put <= 1e-10):
    print("Put spread premium monotonic non‑increasing.")
else:
    print("Put spread premium NOT monotonic.")
    print("Differences:", diff_put[:5])

# Print boundary spots at t=0
zero_call_t0 = find_zero(spots, prem_call_t0)
zero_put_t0 = find_zero(spots, prem_put_t0)
print("\nBoundary at t=0:")
if zero_call_t0 is not None:
    print(f"  Call spread: spot ≥ {zero_call_t0:.2f} → unwind")
else:
    print("  Call spread: no zero crossing in range.")
if zero_put_t0 is not None:
    print(f"  Put spread: spot ≤ {zero_put_t0:.2f} → unwind")
else:
    print("  Put spread: no zero crossing in range.")