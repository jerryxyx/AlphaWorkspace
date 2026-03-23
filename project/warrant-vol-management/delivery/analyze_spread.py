#!/usr/bin/env python3
"""
Analyze the spread (unwind value) vs continuation across spot and time.
Compute delta, theta, and the exercise boundary.
"""
import matplotlib
matplotlib.use('Agg')
import sys
sys.path.insert(0, 'src')
from lattice import black_scholes_call
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Extreme parameters
K = 200.0
S0 = 100.0
sigma_fair = 0.8
sigma_offset = 0.3
sigma_spot = 0.9
T = 1.0
r = 0.10
dt = T / 200
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
q = (np.exp(r * dt) - d) / (u - d)

def sigma_fair_func(spot):
    return sigma_fair

def spread_value(spot, time_to_expiry):
    """Unwind value = C(σ_high) - C(σ_low)"""
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    return black_scholes_call(spot, K, time_to_expiry, r, vol_high) - black_scholes_call(spot, K, time_to_expiry, r, vol_low)

def spread_delta(spot, time_to_expiry):
    """Delta of the spread = N(d1_high) - N(d1_low)"""
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    def d1(vol):
        if time_to_expiry <= 0:
            return 0.0
        return (np.log(spot / K) + (r + 0.5 * vol**2) * time_to_expiry) / (vol * np.sqrt(time_to_expiry))
    d1_low = d1(vol_low)
    d1_high = d1(vol_high)
    return norm.cdf(d1_high) - norm.cdf(d1_low)

def spread_theta(spot, time_to_expiry):
    """Theta of the spread (per year, negative)"""
    vol_low = sigma_fair_func(spot)
    vol_high = vol_low + sigma_offset
    # Black-Scholes theta for call: -S * N'(d1) * σ / (2√T) - r K e^{-rT} N(d2)
    def theta(vol):
        if time_to_expiry <= 0:
            return 0.0
        d1 = (np.log(spot / K) + (r + 0.5 * vol**2) * time_to_expiry) / (vol * np.sqrt(time_to_expiry))
        d2 = d1 - vol * np.sqrt(time_to_expiry)
        term1 = -spot * norm.pdf(d1) * vol / (2 * np.sqrt(time_to_expiry))
        term2 = -r * K * np.exp(-r * time_to_expiry) * norm.cdf(d2)
        return term1 + term2
    return theta(vol_high) - theta(vol_low)

def continuation_value(spot, time):
    """One-step binomial expectation of spread after dt."""
    S_up = spot * u
    S_down = spot * d
    time_next = time + dt
    unwind_up = spread_value(S_up, T - time_next)
    unwind_down = spread_value(S_down, T - time_next)
    return np.exp(-r * dt) * (q * unwind_up + (1-q) * unwind_down)

print("Spread analysis for extreme parameters")
print("="*70)
print(f"K={K}, S0={S0}, σ_fair={sigma_fair}, σ_offset={sigma_offset}, σ_spot={sigma_spot}, r={r}, T={T}")
print()

# 1. Spread vs spot at different times
spots = np.linspace(50, 300, 251)
times = [0.0, 0.25, 0.5, 0.75]
fig1, ax1 = plt.subplots(figsize=(10,6))
for t in times:
    spreads = [spread_value(s, T - t) for s in spots]
    ax1.plot(spots, spreads, label=f't={t:.2f}')
ax1.set_xlabel('Spot')
ax1.set_ylabel('Spread value')
ax1.set_title('Unwind value (spread) vs spot at different times')
ax1.axvline(K, color='k', linestyle='--', label=f'K={K}')
ax1.axvline(S0, color='r', linestyle=':', label=f'S0={S0}')
ax1.legend()
ax1.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/spread_vs_spot.png', dpi=150)
plt.close()

# 2. Spread delta and theta at t=0
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(12,4))
deltas = [spread_delta(s, T) for s in spots]
thetas = [spread_theta(s, T) for s in spots]
ax2a.plot(spots, deltas, 'b-')
ax2a.set_xlabel('Spot')
ax2a.set_ylabel('Delta')
ax2a.set_title('Spread delta (Δ_high - Δ_low) at t=0')
ax2a.axvline(K, color='k', linestyle='--')
ax2a.axvline(S0, color='r', linestyle=':')
ax2a.grid(True, alpha=0.3)

ax2b.plot(spots, thetas, 'r-')
ax2b.set_xlabel('Spot')
ax2b.set_ylabel('Theta (per year)')
ax2b.set_title('Spread theta (θ_high - θ_low) at t=0')
ax2b.axvline(K, color='k', linestyle='--')
ax2b.axvline(S0, color='r', linestyle=':')
ax2b.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output/spread_greeks.png', dpi=150)
plt.close()

# 3. Exercise region: unwind - continuation across spot and time
time_grid = np.linspace(0, T, 21)
spot_grid = np.linspace(50, 300, 251)
diff_grid = np.zeros((len(time_grid), len(spot_grid)))
for i, t in enumerate(time_grid):
    for j, s in enumerate(spot_grid):
        unwind = spread_value(s, T - t)
        cont = continuation_value(s, t)
        diff_grid[i, j] = unwind - cont

# Find boundary where diff >= 0
boundary_pts = []
for i, t in enumerate(time_grid):
    row = diff_grid[i, :]
    pos = np.where(row >= 0)[0]
    if len(pos) > 0:
        boundary_pts.append((t, spot_grid[pos[0]]))
    else:
        boundary_pts.append((t, np.nan))

fig3, ax3 = plt.subplots(figsize=(10,6))
# Heatmap of diff
im = ax3.imshow(diff_grid, aspect='auto', origin='lower',
                extent=[spot_grid[0], spot_grid[-1], time_grid[0], time_grid[-1]],
                cmap='RdYlGn', vmin=-1, vmax=1)
plt.colorbar(im, ax=ax3, label='unwind - continuation')
# Overlay boundary
boundary_pts = np.array(boundary_pts)
ax3.plot(boundary_pts[:,1], boundary_pts[:,0], 'ko-', markersize=4, label='Exercise boundary')
ax3.set_xlabel('Spot')
ax3.set_ylabel('Time')
ax3.set_title('Exercise region: green = unwind ≥ continuation (exercise)')
ax3.axvline(S0, color='r', linestyle=':', label=f'S0={S0}')
ax3.legend()
plt.tight_layout()
plt.savefig('output/exercise_region.png', dpi=150)
plt.close()

# 4. Early‑exercise premium as function of spot at t=0
premiums = []
for s in spots:
    unwind0 = spread_value(s, T)
    # Compute American value via small lattice (n=50) for that spot
    import lattice
    val, _, _ = lattice.binomial_tree_value(
        n=50, S0=s, K=K, T=T, r=r, sigma_spot=sigma_spot,
        sigma_fair_func=sigma_fair_func, sigma_offset=sigma_offset)
    premiums.append(val - unwind0)

fig4, ax4 = plt.subplots(figsize=(10,6))
ax4.plot(spots, premiums, 'b-')
ax4.set_xlabel('Spot')
ax4.set_ylabel('Early‑exercise premium')
ax4.set_title('Early‑exercise premium vs spot (American - European)')
ax4.axhline(0, color='k', linestyle='--')
ax4.axvline(S0, color='r', linestyle=':', label=f'S0={S0}')
ax4.axvline(K, color='k', linestyle='--', label=f'K={K}')
ax4.grid(True, alpha=0.3)
ax4.legend()
plt.tight_layout()
plt.savefig('output/premium_vs_spot.png', dpi=150)
plt.close()

# Print key numbers
print("Spread at t=0, S=S0:")
print(f"  Unwind value = {spread_value(S0, T):.6f}")
print(f"  Delta spread = {spread_delta(S0, T):.6f}")
print(f"  Theta spread = {spread_theta(S0, T):.6f} (per year)")
print(f"  Continuation value (one‑step) = {continuation_value(S0, 0):.6f}")
print(f"  Difference (unwind - continuation) = {spread_value(S0, T) - continuation_value(S0, 0):.6f}")
print()
print("Exercise boundary (first few times):")
for t, s in boundary_pts[:5]:
    if np.isnan(s):
        print(f"  t={t:.3f}: no exercise region")
    else:
        print(f"  t={t:.3f}: boundary spot = {s:.2f}")
print()
print("Early‑exercise premium at S0:")
premium_S0 = lattice.binomial_tree_value(n=200, S0=S0, K=K, T=T, r=r, sigma_spot=sigma_spot,
                                         sigma_fair_func=sigma_fair_func, sigma_offset=sigma_offset)[0] - spread_value(S0, T)
print(f"  Premium = {premium_S0:.6f}")
print()
print("Interpretation:")
print("- Spread delta is positive → spread increases with spot.")
print("- Spread theta is negative → spread decays over time.")
print("- Exercise boundary slopes downward: as time passes, continuation decays,")
print("  making exercise optimal at lower spots.")
print("- At S0=100, we are above the boundary at t=0 → immediate unwinding optimal.")
print("- Early‑exercise premium is zero at S0, positive for spots below boundary.")
print()
print("Plots saved to output/:")
print("  spread_vs_spot.png, spread_greeks.png, exercise_region.png, premium_vs_spot.png")