#!/usr/bin/env python3
"""
Analyze exercise‑flag patterns to detect one or two boundaries.
Parameters: σ_fair 0.20–0.40 step 0.01 (21), σ_offset 0.00–0.10 step 0.01 (11), S0=K=100, T=1, r=0.05, σ_spot = σ_fair.
Use lattice with n=100, examine exercise flags at each time step, classify pattern.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np
import pandas as pd

K = 100.0
S0 = 100.0
T = 1.0
r = 0.05
n = 100   # time steps

# Parameter ranges
sigma_fair_vals = np.linspace(0.20, 0.40, 21)   # 0.20,0.21,...,0.40
sigma_offset_vals = np.linspace(0.00, 0.10, 11)  # 0.00,0.01,...,0.10

def classify_pattern(spots, ex):
    """
    spots: array of spots at a given time step (descending order, highest first)
    ex: boolean array same length, True where exercise optimal.
    Returns pattern string and boundaries.
    """
    if np.all(ex):
        return 'always', None, None
    if np.all(~ex):
        return 'never', None, None
    
    # Find contiguous exercise regions
    changes = np.diff(ex.astype(int))
    starts = np.where(changes == 1)[0] + 1   # index where ex becomes True
    ends = np.where(changes == -1)[0]        # index where ex becomes False
    # Handle edge cases
    if ex[0]:
        starts = np.insert(starts, 0, 0)
    if ex[-1]:
        ends = np.append(ends, len(ex)-1)
    
    if len(starts) == 0 or len(ends) == 0:
        # Should not happen
        return 'unknown', None, None
    
    # Currently we expect at most two regions (call spread: exercise at high spots)
    # For call spread, exercise region is at high spots (low indices).
    # For put spread, exercise region is at low spots (high indices).
    # We'll just detect number of regions.
    regions = []
    for s, e in zip(starts, ends):
        if s <= e:
            regions.append((spots[e], spots[s]))  # lower, upper (since spots descending)
    
    if len(regions) == 1:
        lower, upper = regions[0]
        # Determine if region is at high end or low end
        if ex[0]:  # exercise at highest spot
            return 'lower_only', lower, np.inf
        else:
            return 'upper_only', -np.inf, upper
    elif len(regions) == 2:
        # Two separate regions (unlikely)
        return 'two_regions', regions[0][0], regions[1][1]
    else:
        # More regions
        return f'multiple_{len(regions)}', regions[0][0], regions[-1][1]

# Results storage
results = []

print("Starting boundary pattern analysis...")
total = len(sigma_fair_vals) * len(sigma_offset_vals) * 2
count = 0

for sigma_fair in sigma_fair_vals:
    sigma_spot = sigma_fair
    def sigma_fair_func(spot):
        return sigma_fair
    for sigma_offset in sigma_offset_vals:
        for option_type in ('call', 'put'):
            count += 1
            if count % 50 == 0:
                print(f"  Progress: {count}/{total}")
            
            # Run lattice
            amer, boundary, exercise_flags = lattice.binomial_tree_value(
                n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type=option_type)
            
            # European value
            if option_type == 'call':
                euro = lattice.black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(S0, K, T, r, sigma_fair)
            else:
                euro = lattice.black_scholes_put(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(S0, K, T, r, sigma_fair)
            early_premium = amer - euro
            
            # Analyze pattern at each time step, focus on t=0 (step 0) and mid‑life (step n//2)
            # At step 0 there is only one spot (S0), pattern trivial.
            # We'll look at step n//2 where tree has many nodes.
            step = n // 2
            # Reconstruct spots at that step (same as inside lattice)
            dt = T / n
            u = np.exp(sigma_spot * np.sqrt(dt))
            d = 1.0 / u
            spots_step = S0 * (u ** np.arange(step, -1, -1)) * (d ** np.arange(0, step+1))  # descending
            ex = exercise_flags[step]
            pattern, lower, upper = classify_pattern(spots_step, ex)
            
            # Also count zero crossings via premium (as sanity)
            # Use coarse spot grid for zero crossing detection
            spots_grid = np.linspace(50, 150, 51)
            prem = []
            for s in spots_grid:
                if option_type == 'call':
                    unwind = lattice.black_scholes_call(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
                else:
                    unwind = lattice.black_scholes_put(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(s, K, T, r, sigma_fair)
                # Continuation using small tree (n_small=10)
                dt_small = T / 10
                u_small = np.exp(sigma_spot * np.sqrt(dt_small))
                d_small = 1.0 / u_small
                q_small = (np.exp(r * dt_small) - d_small) / (u_small - d_small)
                val_up, _, _ = lattice.binomial_tree_value(
                    9, s * u_small, K, T - dt_small, r, sigma_spot, sigma_fair_func,
                    sigma_offset, option_type=option_type)
                val_down, _, _ = lattice.binomial_tree_value(
                    9, s * d_small, K, T - dt_small, r, sigma_spot, sigma_fair_func,
                    sigma_offset, option_type=option_type)
                cont = np.exp(-r * dt_small) * (q_small * val_up + (1 - q_small) * val_down)
                prem.append(unwind - cont)
            # Count zero crossings
            zeros = []
            for i in range(len(spots_grid)-1):
                if prem[i] * prem[i+1] <= 0:
                    x0, x1 = spots_grid[i], spots_grid[i+1]
                    y0, y1 = prem[i], prem[i+1]
                    if abs(y1 - y0) < 1e-12:
                        zero = (x0 + x1) / 2
                    else:
                        zero = x0 - y0 * (x1 - x0) / (y1 - y0)
                    zeros.append(zero)
            num_zeros = len(zeros)
            
            results.append({
                'sigma_fair': sigma_fair,
                'sigma_offset': sigma_offset,
                'option_type': option_type,
                'pattern': pattern,
                'lower_boundary': lower,
                'upper_boundary': upper,
                'num_zeros': num_zeros,
                'early_exercise_premium': early_premium,
                'american_value': amer,
                'european_value': euro,
            })

# Convert to DataFrame
df = pd.DataFrame(results)
csv_path = 'output/boundary_pattern_results.csv'
df.to_csv(csv_path, index=False)
print(f"\n✅ Results saved to {csv_path}")

# Summary
print("\n=== Summary ===")
print(f"Total combos: {len(df)}")
print("\nPattern distribution:")
print(df['pattern'].value_counts())
print("\nNumber of zero crossings distribution:")
print(df['num_zeros'].value_counts().sort_index())

# Cross‑tabulate pattern vs zero crossings
cross = pd.crosstab(df['pattern'], df['num_zeros'])
print("\nPattern vs zero‑crossing count:")
print(cross)

# Check for combos with two zeros (possible finite range)
two_zeros = df[df['num_zeros'] == 2]
if len(two_zeros) > 0:
    print(f"\nFound {len(two_zeros)} combos with two zero crossings (possible finite range):")
    print(two_zeros[['sigma_fair','sigma_offset','option_type','pattern','lower_boundary','upper_boundary']].head(10))
else:
    print("\nNo combos with two zero crossings.")

# For each sigma_fair, count patterns
print("\nPatterns per σ_fair (call spreads only):")
call_df = df[df['option_type']=='call']
for sf in sigma_fair_vals:
    subset = call_df[abs(call_df['sigma_fair'] - sf) < 1e-6]
    if len(subset) > 0:
        patterns = subset['pattern'].value_counts()
        print(f"σ_fair={sf:.2f}: {patterns.to_dict()}")

# Save aggregated summary
summary = df.groupby(['sigma_fair','option_type']).agg({
    'pattern': lambda x: x.mode()[0] if len(x) > 0 else None,
    'num_zeros': lambda x: x.mode()[0],
    'early_exercise_premium': 'mean',
}).reset_index()
summary.to_csv('output/boundary_summary.csv', index=False)
print("\n✅ Summary saved to output/boundary_summary.csv")