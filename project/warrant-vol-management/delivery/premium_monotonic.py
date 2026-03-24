#!/usr/bin/env python3
"""
Plot unwind premium (unwind - continuation) across spots for call spreads and put spreads.
Check monotonicity and breakeven point.
"""
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def black_scholes_put(spot, strike, time_to_expiry, risk_free_rate, volatility):
    """European put price via Black-Scholes formula."""
    if time_to_expiry <= 0.0:
        return max(strike - spot, 0.0)
    d1 = (np.log(spot / strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) \
         / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)
    return strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - spot * norm.cdf(-d1)

# Parameters (extreme case)
K = 200.0
S0 = 100.0
sigma_fair = 0.8
sigma_offset = 0.3
sigma_spot = 0.9
T = 1.0
r = 0.10
n = 200
dt = T / n
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)

def sigma_fair_func(spot):
    return sigma_fair

def unwind_call_spread(spot, time_to_expiry):
    """Call spread: long high-vol call, short low-vol call."""
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    C_high = black_scholes_call(spot, K, time_to_expiry, r, vol_high)
    C_low = black_scholes_call(spot, K, time_to_expiry, r, vol_low)
    return C_high - C_low

def unwind_put_spread(spot, time_to_expiry):
    """Put spread: long high-vol put, short low-vol put."""
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    P_high = black_scholes_put(spot, K, time_to_expiry, r, vol_high)
    P_low = black_scholes_put(spot, K, time_to_expiry, r, vol_low)
    return P_high - P_low

def continuation_value(spot, time, unwind_func):
    """
    Compute continuation value at (spot, time) using a two‑step tree.
    unwind_func is either unwind_call_spread or unwind_put_spread.
    """
    # Possible spots after dt
    S_up = spot * u
    S_down = spot * d
    time_next = time + dt
    time_next2 = time + 2*dt
    
    # Unwind values at time+2*dt
    unwind_up_up = unwind_func(S_up * u, T - time_next2)
    unwind_up_down = unwind_func(S_up * d, T - time_next2)
    unwind_down_down = unwind_func(S_down * d, T - time_next2)
    
    # Option values at time+dt = max(unwind, continuation from t=dt to t=2dt)
    # For simplicity, assume continuation from dt to 2dt is zero (close to maturity).
    # This approximation is fine for monotonicity check.
    unwind_up = unwind_func(S_up, T - time_next)
    unwind_down = unwind_func(S_down, T - time_next)
    option_up = unwind_up
    option_down = unwind_down
    
    # Continuation at current node = discounted expectation
    continuation = np.exp(-r * dt) * (q * option_up + (1-q) * option_down)
    return continuation

# Range of spots
spots = np.linspace(50, 300, 251)

# Times to examine
times = [0.0, 0.25, 0.5, 0.75]

# Plot call spread premium
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for idx, t in enumerate(times):
    ax = axes[idx]
    premium_call = []
    premium_put = []
    for s in spots:
        unwind_call = unwind_call_spread(s, T - t)
        cont_call = continuation_value(s, t, unwind_call_spread)
        premium_call.append(unwind_call - cont_call)
        
        unwind_put = unwind_put_spread(s, T - t)
        cont_put = continuation_value(s, t, unwind_put_spread)
        premium_put.append(unwind_put - cont_put)
    
    ax.plot(spots, premium_call, 'b-', label='Call spread premium')
    ax.plot(spots, premium_put, 'r-', label='Put spread premium')
    ax.axhline(0, color='k', linestyle='--', linewidth=0.8)
    ax.axvline(K, color='g', linestyle=':', label=f'K={K}')
    ax.set_xlabel('Spot')
    ax.set_ylabel('Unwind - Continuation')
    ax.set_title(f't = {t:.2f}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Find breakeven points where premium crosses zero
    # For calls: find first spot where premium >= 0 (lowest spot)
    # For puts: find last spot where premium >= 0 (highest spot)
    # Use linear interpolation
    def find_zero_crossing(x, y):
        for i in range(len(x)-1):
            if y[i] * y[i+1] <= 0:
                # linear interpolation
                x0 = x[i]
                x1 = x[i+1]
                y0 = y[i]
                y1 = y[i+1]
                if abs(y1 - y0) < 1e-12:
                    return (x0 + x1) / 2
                return x0 - y0 * (x1 - x0) / (y1 - y0)
        return None
    
    zero_call = find_zero_crossing(spots, premium_call)
    zero_put = find_zero_crossing(spots, premium_put)
    
    if zero_call is not None:
        ax.axvline(zero_call, color='b', linestyle='--', linewidth=0.8, label=f'Call boundary={zero_call:.1f}')
    if zero_put is not None:
        ax.axvline(zero_put, color='r', linestyle='--', linewidth=0.8, label=f'Put boundary={zero_put:.1f}')

plt.tight_layout()
plt.savefig('output/premium_monotonic.png', dpi=150)
plt.close()

print("=== Summary ===")
print("Call spread premium (unwind - continuation) should be monotonic increasing with spot.")
print("Put spread premium should be monotonic decreasing with spot.")
print("Breakeven point (premium=0) defines the exercise boundary:")
print("  - For calls: lowest spot where premium ≥ 0 (exercise above).")
print("  - For puts: highest spot where premium ≥ 0 (exercise below).")
print()
print("Plots show premium across spots for four times.")
print("Zero crossings (vertical dashed lines) indicate boundary spots.")
print("Plot saved to output/premium_monotonic.png")

# Additional check: monotonicity
print("\n=== Monotonicity check at t=0 ===")
premium_call_t0 = []
premium_put_t0 = []
for s in spots:
    unwind_call = unwind_call_spread(s, T)
    cont_call = continuation_value(s, 0.0, unwind_call_spread)
    premium_call_t0.append(unwind_call - cont_call)
    
    unwind_put = unwind_put_spread(s, T)
    cont_put = continuation_value(s, 0.0, unwind_put_spread)
    premium_put_t0.append(unwind_put - cont_put)

# Check monotonicity: difference between consecutive values
diff_call = np.diff(premium_call_t0)
diff_put = np.diff(premium_put_t0)
if np.all(diff_call >= -1e-10):
    print("Call spread premium is monotonic non‑decreasing.")
else:
    print("Call spread premium is NOT monotonic (check).")
if np.all(diff_put <= 1e-10):
    print("Put spread premium is monotonic non‑increasing.")
else:
    print("Put spread premium is NOT monotonic (check).")

# Print boundary spots at t=0
zero_call_t0 = find_zero_crossing(spots, premium_call_t0)
zero_put_t0 = find_zero_crossing(spots, premium_put_t0)
print(f"\nBoundary at t=0:")
if zero_call_t0 is not None:
    print(f"  Call spread: spot ≥ {zero_call_t0:.2f} → unwind")
else:
    print(f"  Call spread: no zero crossing in range.")
if zero_put_t0 is not None:
    print(f"  Put spread: spot ≤ {zero_put_t0:.2f} → unwind")
else:
    print(f"  Put spread: no zero crossing in range.")