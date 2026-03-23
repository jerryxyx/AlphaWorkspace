#!/usr/bin/env python3
"""
Demo binomial tree visualization with extreme parameters.
"""
import sys
sys.path.insert(0, 'src')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from lattice import black_scholes_call

def plot_binomial_tree_extreme(n_steps=5):
    # Extreme parameters from user
    K = 200.0
    S0 = 100.0
    sigma_fair = 0.8
    sigma_offset = 0.3
    sigma_spot = 0.9
    T = 1.0
    r = 0.10
    
    def sigma_fair_func(spot):
        return sigma_fair  # constant
    
    # Build tree
    dt = T / n_steps
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    q = (np.exp(r * dt) - d) / (u - d)
    
    spots = {}
    for i in range(n_steps + 1):
        for j in range(i + 1):
            spots[(i, j)] = S0 * (u ** (i - j)) * (d ** j)
    
    unwind = {}
    for (i, j), spot in spots.items():
        time_to_expiry = T - i * dt
        vol_low = sigma_fair_func(spot)
        vol_high = vol_low + sigma_offset
        price_low = black_scholes_call(spot, K, time_to_expiry, r, vol_low)
        price_high = black_scholes_call(spot, K, time_to_expiry, r, vol_high)
        unwind[(i, j)] = price_high - price_low
    
    value = {}
    exercise = {}
    # Maturity
    for j in range(n_steps + 1):
        value[(n_steps, j)] = unwind[(n_steps, j)]
        exercise[(n_steps, j)] = True
    
    # Backward
    for i in range(n_steps - 1, -1, -1):
        for j in range(i + 1):
            continuation = np.exp(-r * dt) * (q * value[(i+1, j)] + (1-q) * value[(i+1, j+1)])
            value[(i, j)] = max(unwind[(i, j)], continuation)
            exercise[(i, j)] = unwind[(i, j)] >= continuation
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Edges
    for i in range(n_steps):
        for j in range(i + 1):
            x0, y0 = i, spots[(i, j)]
            ax.plot([x0, i+1], [y0, spots[(i+1, j)]], 'k-', alpha=0.3, linewidth=0.8)
            ax.plot([x0, i+1], [y0, spots[(i+1, j+1)]], 'k-', alpha=0.3, linewidth=0.8)
    
    # Nodes with color
    node_x, node_y, colors = [], [], []
    for (i, j), spot in spots.items():
        node_x.append(i)
        node_y.append(spot)
        colors.append('limegreen' if exercise[(i, j)] else 'tomato')
    ax.scatter(node_x, node_y, c=colors, s=150, edgecolors='black', linewidth=1, zorder=10)
    
    # Annotate values
    for (i, j), spot in spots.items():
        if i <= 3:  # avoid clutter
            ax.annotate(f"{value[(i, j)]:.2f}", (i, spot), xytext=(0, 12),
                        textcoords='offset points', ha='center', fontsize=9,
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
    
    ax.set_xlabel('Time Step', fontsize=12)
    ax.set_ylabel('Spot Price', fontsize=12)
    ax.set_title(f'Binomial Tree (σ_fair={sigma_fair}, σ_spot={sigma_spot}, σ_offset={sigma_offset})\\nGreen=Exercise, Red=Wait', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='limegreen', edgecolor='black', label='Exercise (Unwind)'),
        Patch(facecolor='tomato', edgecolor='black', label='Wait (Continue)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig('output/binomial_tree_extreme.png', dpi=150)
    plt.close()
    print(f"Tree plot saved to output/binomial_tree_extreme.png")
    print(f"Initial value: {value[(0,0)]:.6f}")
    print(f"Unwind at root: {unwind[(0,0)]:.6f}")
    print(f"Exercise at root? {exercise[(0,0)]}")
    return value, exercise, spots

if __name__ == '__main__':
    plot_binomial_tree_extreme(n_steps=5)