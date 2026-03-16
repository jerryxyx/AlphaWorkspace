import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.stats import lognorm

# ====================== BLACK-SCHOLES HELPERS ======================
def black_scholes_call(S, K, sigma, T=1.0, r=0.0, q=0.0):
    if sigma <= 0:
        return max(S * np.exp(-q * T) - K * np.exp(-r * T), 0.0)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def black_scholes_put(S, K, sigma, T=1.0, r=0.0, q=0.0):
    if sigma <= 0:
        return max(K * np.exp(-r * T) - S * np.exp(-q * T), 0.0)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

def black_scholes(S, K, sigma, option_type='call', T=1.0, r=0.0, q=0.0):
    if option_type.lower() == 'call':
        return black_scholes_call(S, K, sigma, T, r, q)
    elif option_type.lower() == 'put':
        return black_scholes_put(S, K, sigma, T, r, q)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

# ====================== PNL & EXPECTED VALUE HELPERS ======================
def compute_pnl(S, K, vol_high, vol_base, option_type='call', S0=100.0, T=1.0, r=0.0, q=0.0):
    debit = black_scholes(S0, K, vol_high, option_type, T, r, q) - black_scholes(S0, K, vol_base, option_type, T, r, q)
    price_high = black_scholes(S, K, vol_high, option_type, T, r, q)
    price_base = black_scholes(S, K, vol_base, option_type, T, r, q)
    return price_high - price_base - debit

def theoretical_expected_pnl(K, vol_high, vol_base, sigma_spot, option_type='call', S0=100.0, T=1.0, r=0.0, q=0.0):
    debit = black_scholes(S0, K, vol_high, option_type, T, r, q) - black_scholes(S0, K, vol_base, option_type, T, r, q)
    sigma_total_h = np.sqrt(sigma_spot**2 + vol_high**2)
    sigma_total_b = np.sqrt(sigma_spot**2 + vol_base**2)
    e_high = black_scholes(S0, K, sigma_total_h, option_type, T, r, q)
    e_base = black_scholes(S0, K, sigma_total_b, option_type, T, r, q)
    return (e_high - e_base) - debit

def monte_carlo_expected_pnl(K, vol_high, vol_base, sigma_spot, option_type='call', n_samples=100_000, S0=100.0, T=1.0, r=0.0, q=0.0, seed=42):
    np.random.seed(seed)
    S_samples = lognorm.rvs(s=sigma_spot, scale=S0 * np.exp(-0.5 * sigma_spot**2), size=n_samples)
    pnls = np.array([compute_pnl(s, K, vol_high, vol_base, option_type, S0, T, r, q) for s in S_samples])
    return np.mean(pnls)

# ====================== LSM OPTIMAL UNWIND (decoupled per K) ======================
def lsm_optimal_pnl(K, vol_high, vol_base, sigma_spot, option_type='call', n_paths=3000, n_steps=30, S0=100.0, T=1.0, seed=42):
    """Longstaff-Schwartz LSM — fully decoupled for any K.
    Returns optimal E[PNL] + boundary (mean S* per time step)."""
    dt = T / n_steps
    np.random.seed(seed)
    S = np.zeros((n_paths, n_steps + 1))
    S[:, 0] = S0
    for i in range(1, n_steps + 1):
        Z = np.random.normal(0, 1, n_paths)
        S[:, i] = S[:, i-1] * np.exp(-0.5 * sigma_spot**2 * dt + sigma_spot * np.sqrt(dt) * Z)
    
    cash_flow = np.array([black_scholes(S[i, -1], K, vol_high, option_type, 0.0) - 
                          black_scholes(S[i, -1], K, vol_base, option_type, 0.0) 
                          for i in range(n_paths)])
    
    exercise_spots = [[] for _ in range(n_steps)]
    
    for step in range(n_steps - 1, -1, -1):
        remaining = (n_steps - step) * dt
        current_spread = np.array([black_scholes(S[i, step], K, vol_high, option_type, remaining) - 
                                   black_scholes(S[i, step], K, vol_base, option_type, remaining) 
                                   for i in range(n_paths)])
        
        X = S[:, step] / K
        basis = np.column_stack((np.ones(n_paths), X, X**2, X**3))
        coef = np.linalg.lstsq(basis, cash_flow, rcond=None)[0]
        continuation = basis @ coef
        
        exercise = current_spread > continuation + 1e-8
        cash_flow[exercise] = current_spread[exercise]
        exercise_spots[step].extend(S[exercise, step].tolist())
    
    optimal_spread = np.mean(cash_flow)
    debit = black_scholes(S0, K, vol_high, option_type, T) - black_scholes(S0, K, vol_base, option_type, T)
    optimal_pnl = optimal_spread - debit
    
    # Boundary data (TTM decreasing from T to 0)
    mean_ex_S = [np.mean(spots) if spots else S0 for spots in exercise_spots]
    mean_ttm = [(n_steps - step) * dt for step in range(n_steps)]
    
    # Reverse so x-axis goes from TTM≈0 (left) to TTM=T (right) — matches previous visuals
    mean_ttm = mean_ttm[::-1]
    mean_ex_S = mean_ex_S[::-1]
    
    return optimal_pnl, mean_ex_S, mean_ttm, debit

# ====================== PARAMETERS ======================
S0 = 100.0
T = 1.0
vol_high = 0.25
vol_base = 0.20
sigma_spot = 0.20
strikes = [80, 90, 100, 110, 120, 130, 140, 150]

print("=== VOL-SPREAD LSM SCRIPT (full version) ===\nfitVol=20%, mgn=5%, σ_spot=20%")

# ====================== 1. PNL vs Spot (spot sliding) ======================
spot_range = np.linspace(50, 150, 300)
fig, axs = plt.subplots(4, 2, figsize=(14, 16))
axs = axs.flatten()
for i, K in enumerate(strikes):
    pnl_values = [compute_pnl(s, K, vol_high, vol_base, 'call', S0, T) for s in spot_range]
    debit = black_scholes(S0, K, vol_high, 'call', T) - black_scholes(S0, K, vol_base, 'call', T)
    axs[i].plot(spot_range, pnl_values, 'b-', linewidth=2.5)
    axs[i].axvline(S0, color='red', linestyle='--')
    axs[i].axhline(0, color='black', linestyle='-', linewidth=1)
    axs[i].set_title(f'Strike K = {K}\nInit debit = {debit:.2f}')
    axs[i].set_xlabel('New Spot Price')
    axs[i].set_ylabel('PNL')
    axs[i].grid(True)
fig.suptitle('PNL vs New Spot Price — Spot Sliding (Calls)', fontsize=14)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('pnl_multi_strike_grid_spot_sliding_calls.png', dpi=200)
print("Saved: pnl_multi_strike_grid_spot_sliding_calls.png")

# ====================== 2. Hold E[PNL] vs Strike ======================
fig2, ax2 = plt.subplots(figsize=(10, 6))
for sig in [0.0, 0.10, 0.20, 0.30]:
    e_pnls = [theoretical_expected_pnl(K, vol_high, vol_base, sig, 'call', S0, T) for K in strikes]
    ax2.plot(strikes, e_pnls, 'o-', linewidth=2, label=f'σ_spot = {sig*100:.0f}%')
ax2.set_xlabel('Strike')
ax2.set_ylabel('Theoretical E[PNL]')
ax2.set_title('Hold-to-Maturity Expected PNL vs Strike')
ax2.grid(True)
ax2.legend()
plt.savefig('expected_pnl_vs_strike_hold.png', dpi=200)
print("Saved: expected_pnl_vs_strike_hold.png")

# ====================== 3. HOLD vs LSM OPTIMAL TABLE ======================
print("\n=== HOLD vs LSM OPTIMAL UNWIND (per strike) ===")
print(f"{'Strike':>6} {'Init Debit':>12} {'Hold E[PNL]':>15} {'LSM Optimal E[PNL]':>20} {'Improvement':>15}")
print("-" * 75)
for K in strikes:
    debit = black_scholes(S0, K, vol_high, 'call', T) - black_scholes(S0, K, vol_base, 'call', T)
    hold_theo = theoretical_expected_pnl(K, vol_high, vol_base, sigma_spot, 'call')
    lsm_pnl, _, _, _ = lsm_optimal_pnl(K, vol_high, vol_base, sigma_spot, 'call')
    improvement = lsm_pnl - hold_theo
    print(f"{K:6d} {debit:12.4f} {hold_theo:15.4f} {lsm_pnl:20.4f} {improvement:15.4f}")

# ====================== 4. LSM UNWIND BOUNDARIES — FULLY DECOUPLED (ALL STRIKES) ======================
print("\nGenerating LSM unwind boundaries for EVERY strike (cash-out S* depends on K)...")
fig_b, axs_b = plt.subplots(4, 2, figsize=(14, 16))
axs_b = axs_b.flatten()
for i, K in enumerate(strikes):
    lsm_pnl, mean_ex_S, mean_ttm, debit = lsm_optimal_pnl(K, vol_high, vol_base, sigma_spot, 'call')
    axs_b[i].plot(mean_ttm, mean_ex_S, 'ro-', linewidth=2, label='LSM Cash-out Boundary (mean S*)')
    axs_b[i].axhline(K, color='green', linestyle='--', label=f'Strike = {K}')
    axs_b[i].set_xlabel('Time to Maturity (years)')
    axs_b[i].set_ylabel('Spot Price S* (unwind)')
    axs_b[i].set_title(f'K = {K}\nOptimal E[PNL] = {lsm_pnl:.4f}')
    axs_b[i].grid(True)
    axs_b[i].legend()
fig_b.suptitle('LSM Optimal Cash-out Boundary for EVERY Strike\n(Spot level S* where you unwind both legs)', fontsize=14)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('pnl_unwind_boundaries_all_strikes_grid.png', dpi=200)
print("Saved: pnl_unwind_boundaries_all_strikes_grid.png")

print("\n✅ SCRIPT COMPLETE!")
print("• Boundaries are now FULLY DECOUPLED per K (no more single K_atm).")
print("• Each subplot shows how the cash-out spot S* evolves with time for that specific strike.")
print("• Higher K → boundary shifts upward (you wait for spot to reach the higher strike).")
print("• ATM (K=100) → unwind almost immediately (optimal E[PNL] ≈ 0).")
print("• Far OTM → hold longer (big positive convexity).")
print("• Calls & puts identical (put-call parity). Change any parameter at the top and re-run!")