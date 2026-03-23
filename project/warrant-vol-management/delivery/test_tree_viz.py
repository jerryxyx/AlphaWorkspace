#!/usr/bin/env python3
"""
Test the binomial tree visualization function.
"""
import sys
sys.path.insert(0, 'src')
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Define the function from notebook
def plot_binomial_tree(n_steps=5, S0=100.0, K=100.0, T=1.0, r=0.05, sigma_spot=0.2, sigma_fair_func=None, sigma_offset=0.1):
    from lattice import black_scholes_call
    if sigma_fair_func is None:
        sigma_fair_func = lambda s: 0.2
    
    # Build tree structure
    dt = T / n_steps
    u = np.exp(sigma_spot * np.sqrt(dt))
    d = 1.0 / u
    q = (np.exp(r * dt) - d) / (u - d)
    
    # Spot grid
    spots = {}
    for i in range(n_steps + 1):
        for j in range(i + 1):
            spots[(i, j)] = S0 * (u ** (i - j)) * (d ** j)
    
    # Compute unwind values at each node
    unwind = {}
    for (i, j), spot in spots.items():
        time_to_expiry = T - i * dt
        vol_low = sigma_fair_func(spot)
        vol_high = vol_low + sigma_offset
        price_low = black_scholes_call(spot, K, time_to_expiry, r, vol_low)
        price_high = black_scholes_call(spot, K, time_to_expiry, r, vol_high)
        unwind[(i, j)] = price_high - price_low
    
    # Backward induction for derivative values
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
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw edges
    for i in range(n_steps):
        for j in range(i + 1):
            x0 = i
            y0 = spots[(i, j)]
            # Up branch
            x1 = i + 1
            y1 = spots[(i+1, j)]
            ax.plot([x0, x1], [y0, y1], 'k-', alpha=0.3, linewidth=0.8)
            # Down branch
            y2 = spots[(i+1, j+1)]
            ax.plot([x0, x1], [y0, y2], 'k-', alpha=0.3, linewidth=0.8)
    
    # Plot nodes
    node_x = []
    node_y = []
    node_color = []
    for (i, j), spot in spots.items():
        node_x.append(i)
        node_y.append(spot)
        node_color.append('limegreen' if exercise[(i, j)] else 'tomato')
    
    ax.scatter(node_x, node_y, c=node_color, s=120, edgecolors='black', linewidth=0.8, zorder=10)
    
    # Labels
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Spot Price')
    ax.set_title(f'Binomial Tree (First {n_steps} Steps)\\nGreen = Exercise | Red = Wait')
    ax.grid(True, alpha=0.3)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='limegreen', edgecolor='black', label='Exercise (Unwind)'),
        Patch(facecolor='tomato', edgecolor='black', label='Wait (Continue)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig('output/binomial_tree_test.png', dpi=150)
    plt.close()
    print("Plot saved to output/binomial_tree_test.png")
    return value, exercise, spots

# Run test
print("Testing binomial tree visualization...")
value_dict, exercise_dict, spots_dict = plot_binomial_tree(n_steps=5)
print(f"Initial value: {value_dict[(0,0)]:.6f}")
print(f"Root exercise? {exercise_dict[(0,0)]}")
print("Success!")