#!/usr/bin/env python3
"""
Fast analysis of exercise‑flag patterns to detect one or two boundaries.
Only uses lattice exercise flags (no extra premium calculations).
Parameters: σ_fair 0.20–0.40 step 0.01 (21), σ_offset 0.00–0.10 step 0.01 (11), S0=K=100, T=1, r=0.05, σ_spot = σ_fair.
Use lattice with n=50.
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
n = 50   # time steps (enough for pattern detection)

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
        return 'unknown', None, None
    
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
        # Two separate regions (possible finite range)
        return 'two_regions', regions[0][0], regions[1][1]
    else:
        return f'multiple_{len(regions)}', regions[0][0], regions[-1][1]

# Results storage
results = []

print("Starting boundary pattern analysis (fast)...")
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
            
            # Analyze pattern at mid‑life step (n//2)
            step = n // 2
            dt = T / n
            u = np.exp(sigma_spot * np.sqrt(dt))
            d = 1.0 / u
            spots_step = S0 * (u ** np.arange(step, -1, -1)) * (d ** np.arange(0, step+1))  # descending
            ex = exercise_flags[step]
            pattern, lower, upper = classify_pattern(spots_step, ex)
            
            # Also check step near expiry (step n-1) to see if pattern changes
            step2 = n - 1
            spots2 = S0 * (u ** np.arange(step2, -1, -1)) * (d ** np.arange(0, step2+1))
            ex2 = exercise_flags[step2]
            pattern2, _, _ = classify_pattern(spots2, ex2)
            
            results.append({
                'sigma_fair': sigma_fair,
                'sigma_offset': sigma_offset,
                'option_type': option_type,
                'pattern_mid': pattern,
                'pattern_near_expiry': pattern2,
                'lower_boundary': lower,
                'upper_boundary': upper,
                'early_exercise_premium': early_premium,
                'american_value': amer,
                'european_value': euro,
            })

# Convert to DataFrame
df = pd.DataFrame(results)
csv_path = 'output/boundary_pattern_fast.csv'
df.to_csv(csv_path, index=False)
print(f"\n✅ Results saved to {csv_path}")

# Summary
print("\n=== Summary (mid‑life pattern) ===")
print(f"Total combos: {len(df)}")
print("\nPattern distribution:")
print(df['pattern_mid'].value_counts())
print("\nPattern near expiry distribution:")
print(df['pattern_near_expiry'].value_counts())

# Cross‑tabulate call vs put
print("\nCall vs Put patterns (mid):")
call = df[df['option_type']=='call']['pattern_mid'].value_counts()
put = df[df['option_type']=='put']['pattern_mid'].value_counts()
print("Call:", call.to_dict())
print("Put:", put.to_dict())

# Check for two_regions
two = df[df['pattern_mid'] == 'two_regions']
if len(two) > 0:
    print(f"\n⚠️  Found {len(two)} combos with two regions (finite range):")
    print(two[['sigma_fair','sigma_offset','option_type','lower_boundary','upper_boundary']].head(10))
else:
    print("\n✅ No combos with two regions (finite range).")

# For each sigma_fair, count patterns for call spreads
print("\nPatterns per σ_fair (call spreads):")
call_df = df[df['option_type']=='call']
for sf in sigma_fair_vals:
    subset = call_df[abs(call_df['sigma_fair'] - sf) < 1e-6]
    if len(subset) > 0:
        patterns = subset['pattern_mid'].value_counts()
        print(f"σ_fair={sf:.2f}: {patterns.to_dict()}")

# Save aggregated summary
summary = df.groupby(['sigma_fair','option_type']).agg({
    'pattern_mid': lambda x: x.mode()[0] if len(x) > 0 else None,
    'early_exercise_premium': 'mean',
}).reset_index()
summary.to_csv('output/boundary_pattern_summary.csv', index=False)
print("\n✅ Summary saved to output/boundary_pattern_summary.csv")