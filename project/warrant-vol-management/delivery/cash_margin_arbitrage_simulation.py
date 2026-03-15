#!/usr/bin/env python3
"""
Cash‑Margin Arbitrage Simulation: Warrant vs. Listed Option

Assumptions:
1. Warrant and option have identical terms (underlying, strike, expiry, European style).
2. Warrant volatility = option implied volatility + constant margin x (vol‑margin).
3. Warrant is overpriced relative to option by the value of this vol margin.
4. Arbitrage: sell warrant + buy option (cash‑margin position).
5. Unwind when spread narrows or at expiry.

This script simulates price paths and tracks P&L of the arbitrage trade,
including transaction costs, funding cost of short margin, and stop‑loss/exit rules.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ------------------------------
# 1. Black‑Scholes Pricing
# ------------------------------
def black_scholes(S, K, T, r, sigma, option_type='call'):
    """
    European Black‑Scholes price.
    S: spot price
    K: strike price
    T: time to maturity in years
    r: risk‑free rate (continuous)
    sigma: volatility (annualized)
    option_type: 'call' or 'put'
    """
    if T <= 0:
        if option_type == 'call':
            return max(S - K, 0)
        else:
            return max(K - S, 0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return price

def black_scholes_delta(S, K, T, r, sigma, option_type='call'):
    """Delta of European option."""
    if T <= 0:
        return 1.0 if (option_type == 'call' and S > K) else 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option_type == 'call':
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1

def black_scholes_vega(S, K, T, r, sigma):
    """Vega of European option (per 1% change in vol)."""
    if T <= 0:
        return 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return S * norm.pdf(d1) * np.sqrt(T) * 0.01  # vega per 1% vol change

# ------------------------------
# 2. Simulation Parameters
# ------------------------------
np.random.seed(42)  # reproducible results

# Contract terms
S0 = 100.0           # initial spot
K = 100.0            # strike (ATM)
T_years = 0.5        # 6 months to expiry
r = 0.03             # risk‑free rate (3% p.a.)
option_iv = 0.20     # listed option implied volatility (20%)
margin_x = 0.05      # warrant vol margin = 5% points
warrant_iv = option_iv + margin_x  # warrant volatility = 25%

# Trading parameters
trade_size = 1000    # number of contracts (each contract = 1 share)
transaction_cost_per_contract = 0.001  # 0.1% of notional
funding_rate = 0.05  # annual cost of short margin (5% p.a.)
stop_loss_spread = -0.02  # exit if spread widens beyond 2% of spot

# Simulation settings
n_paths = 1000       # number of Monte Carlo paths
n_steps = 126        # daily steps over 6 months (252 days/year)
dt = T_years / n_steps

# ------------------------------
# 3. Generate Underlying Paths (GBM)
# ------------------------------
print("Generating underlying price paths...")
paths = np.zeros((n_paths, n_steps + 1))
paths[:, 0] = S0
for t in range(1, n_steps + 1):
    z = np.random.randn(n_paths)
    paths[:, t] = paths[:, t-1] * np.exp((r - 0.5 * option_iv**2) * dt 
                                         + option_iv * np.sqrt(dt) * z)

# ------------------------------
# 4. Define Entry & Exit Logic
# ------------------------------
def calculate_spread(S, t):
    """Return warrant price - option price (both calls) at time t."""
    T_remaining = T_years - t * dt
    option_price = black_scholes(S, K, T_remaining, r, option_iv, 'call')
    warrant_price = black_scholes(S, K, T_remaining, r, warrant_iv, 'call')
    return warrant_price - option_price

def entry_signal(spread, S):
    """
    Enter arbitrage if spread > entry threshold.
    Threshold = transaction_cost * 2 + small buffer.
    """
    entry_threshold = transaction_cost_per_contract * 2 * S  # 0.2% of spot
    return spread > entry_threshold

def exit_signal(spread, S, entry_spread, days_in_trade):
    """
    Exit conditions:
    1. Spread converges to zero or negative (profit realized).
    2. Spread widens beyond stop‑loss threshold.
    3. Time decay (theta) makes holding unattractive after certain days.
    """
    # Stop‑loss: spread widens by more than stop_loss_spread * S from entry
    if spread - entry_spread > stop_loss_spread * S:
        return 'stop_loss'
    # Take‑profit: spread closes to within 0.05% of spot
    if spread < 0.0005 * S:
        return 'profit'
    # Hold too long (more than 60 days) – force exit
    if days_in_trade > 60:
        return 'timeout'
    return 'hold'

# ------------------------------
# 5. Run Monte Carlo Simulation
# ------------------------------
print("Running Monte Carlo simulation of arbitrage trades...")
results = []

for p in range(n_paths):
    S_path = paths[p]
    # Initial spread at time 0
    spread0 = calculate_spread(S0, 0)
    if not entry_signal(spread0, S0):
        # No trade entered on this path
        continue
    
    # Enter trade at day 0
    entry_day = 0
    entry_spread = spread0
    entry_spot = S0
    position_open = True
    days_in_trade = 0
    
    for t in range(1, n_steps + 1):
        days_in_trade = t - entry_day
        S = S_path[t]
        spread = calculate_spread(S, t)
        
        if not position_open:
            break
        
        # Check exit conditions
        exit_reason = exit_signal(spread, S, entry_spread, days_in_trade)
        if exit_reason != 'hold':
            # Calculate P&L at exit
            T_remaining = T_years - t * dt
            option_price = black_scholes(S, K, T_remaining, r, option_iv, 'call')
            warrant_price = black_scholes(S, K, T_remaining, r, warrant_iv, 'call')
            
            # P&L from option leg (long)
            option_pnl = (option_price - black_scholes(entry_spot, K, T_years, r, option_iv, 'call')) * trade_size
            # P&L from warrant leg (short)
            warrant_pnl = (black_scholes(entry_spot, K, T_years, r, warrant_iv, 'call') - warrant_price) * trade_size
            # Transaction costs (pay twice: entry + exit)
            transaction_cost = transaction_cost_per_contract * entry_spot * trade_size * 2
            # Funding cost of short margin (assuming margin = warrant notional * margin rate)
            margin_notional = warrant_price * trade_size
            funding_cost = margin_notional * funding_rate * (days_in_trade / 252)
            
            total_pnl = option_pnl + warrant_pnl - transaction_cost - funding_cost
            
            results.append({
                'path': p,
                'entry_day': entry_day,
                'exit_day': t,
                'exit_reason': exit_reason,
                'entry_spread': entry_spread,
                'exit_spread': spread,
                'entry_spot': entry_spot,
                'exit_spot': S,
                'option_pnl': option_pnl,
                'warrant_pnl': warrant_pnl,
                'transaction_cost': -transaction_cost,
                'funding_cost': -funding_cost,
                'total_pnl': total_pnl
            })
            position_open = False
            break
    
    # If position still open at expiry
    if position_open:
        t = n_steps
        S = S_path[t]
        spread = calculate_spread(S, t)
        T_remaining = 0.0
        option_price = max(S - K, 0)
        warrant_price = max(S - K, 0)  # same intrinsic value at expiry
        
        option_pnl = (option_price - black_scholes(entry_spot, K, T_years, r, option_iv, 'call')) * trade_size
        warrant_pnl = (black_scholes(entry_spot, K, T_years, r, warrant_iv, 'call') - warrant_price) * trade_size
        transaction_cost = transaction_cost_per_contract * entry_spot * trade_size * 2
        funding_cost = margin_notional * funding_rate * (days_in_trade / 252)
        total_pnl = option_pnl + warrant_pnl - transaction_cost - funding_cost
        
        results.append({
            'path': p,
            'entry_day': entry_day,
            'exit_day': t,
            'exit_reason': 'expiry',
            'entry_spread': entry_spread,
            'exit_spread': spread,
            'entry_spot': entry_spot,
            'exit_spot': S,
            'option_pnl': option_pnl,
            'warrant_pnl': warrant_pnl,
            'transaction_cost': -transaction_cost,
            'funding_cost': -funding_cost,
            'total_pnl': total_pnl
        })

# ------------------------------
# 6. Analyze Results
# ------------------------------
if results:
    df = pd.DataFrame(results)
    print(f"\nTrades executed: {len(df)}")
    print("\nExit reason counts:")
    print(df['exit_reason'].value_counts())
    print("\nP&L summary (total per trade):")
    print(df['total_pnl'].describe())
    print(f"\nAverage P&L per trade: ${df['total_pnl'].mean():.2f}")
    print(f"Win rate: {(df['total_pnl'] > 0).sum() / len(df):.1%}")
    
    # Plot histogram of P&L
    plt.figure(figsize=(10, 6))
    plt.hist(df['total_pnl'], bins=30, edgecolor='black', alpha=0.7)
    plt.axvline(x=0, color='red', linestyle='--', label='Breakeven')
    plt.xlabel('Trade P&L ($)')
    plt.ylabel('Frequency')
    plt.title('Cash‑Margin Arbitrage P&L Distribution')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig('/tmp/cash_margin_arbitrage_pnl.png', dpi=150)
    print("\nP&L histogram saved to /tmp/cash_margin_arbitrage_pnl.png")
    
    # Plot sample path with trade entry/exit
    sample_path = 0
    if sample_path < n_paths:
        S_sample = paths[sample_path]
        spreads = [calculate_spread(S_sample[t], t) for t in range(n_steps + 1)]
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(S_sample, label='Underlying price')
        plt.axhline(y=K, color='gray', linestyle=':', label='Strike')
        plt.ylabel('Spot')
        plt.title(f'Sample Path {sample_path}: Underlying Price')
        plt.legend()
        plt.grid(alpha=0.3)
        
        plt.subplot(2, 1, 2)
        plt.plot(spreads, label='Warrant‑Option spread')
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        # Mark entry/exit if trade occurred on this path
        path_trades = df[df['path'] == sample_path]
        for _, trade in path_trades.iterrows():
            plt.axvline(x=trade['entry_day'], color='green', linestyle='--', label='Entry' if _ == path_trades.index[0] else '')
            plt.axvline(x=trade['exit_day'], color='red', linestyle='--', label='Exit' if _ == path_trades.index[0] else '')
        plt.xlabel('Trading day')
        plt.ylabel('Spread ($)')
        plt.title('Warrant‑Option Price Spread')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('/tmp/cash_margin_sample_path.png', dpi=150)
        print("Sample path plot saved to /tmp/cash_margin_sample_path.png")
else:
    print("No trades entered under current parameters (entry threshold too high).")

# ------------------------------
# 7. Sensitivity Analysis
# ------------------------------
print("\n--- Sensitivity Analysis ---")
print("Varying vol margin (x):")
for x in [0.02, 0.05, 0.08, 0.10]:
    warrant_iv_test = option_iv + x
    spread0_test = black_scholes(S0, K, T_years, r, warrant_iv_test, 'call') - black_scholes(S0, K, T_years, r, option_iv, 'call')
    print(f"  margin x = {x:.2f}: initial spread = ${spread0_test:.4f}")

print("\nVarying transaction cost:")
for tc in [0.0005, 0.001, 0.002]:
    entry_threshold = tc * 2 * S0
    print(f"  tc = {tc:.4f}: entry threshold = ${entry_threshold:.4f}")

print("\n--- Key Takeaways ---")
print("1. Entry requires warrant‑option spread > transaction costs + buffer.")
print("2. Exit triggers: spread convergence (profit), stop‑loss, or timeout.")
print("3. Funding cost of short margin reduces profitability.")
print("4. Higher vol margin increases spread and profit potential.")
print("5. Real‑world complexities: liquidity, short‑selling constraints, margin haircuts.")

# ------------------------------
# 8. Export Results
# ------------------------------
if results:
    df.to_csv('/tmp/cash_margin_arbitrage_results.csv', index=False)
    print("\nDetailed results saved to /tmp/cash_margin_arbitrage_results.csv")

print("\nSimulation complete.")