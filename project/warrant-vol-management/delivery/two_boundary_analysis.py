#!/usr/bin/env python3
"""
Determine if call/put spreads have one or two exercise boundaries (i.e., a finite range).
Parameters: σ_fair 0.20–0.40 step 0.01 (21), σ_offset 0.00–0.10 step 0.01 (11), S0=K=100, T=1, r=0.05, σ_spot = σ_fair.
For each combo, compute premium across spots 50–150, count zero crossings, classify boundary type.
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
# Spot grid for premium evaluation
spots = np.linspace(50, 150, 201)  # fine enough to detect zero crossings

# Parameter ranges
sigma_fair_vals = np.linspace(0.20, 0.40, 21)   # 0.20,0.21,...,0.40
sigma_offset_vals = np.linspace(0.00, 0.10, 11)  # 0.00,0.01,...,0.10

# Results storage
results = []

print("Starting two‑boundary analysis...")
total = len(sigma_fair_vals) * len(sigma_offset_vals) * 2
count = 0

for sigma_fair in sigma_fair_vals:
    sigma_spot = sigma_fair  # assume spot vol equals implied vol
    def sigma_fair_func(spot):
        return sigma_fair
    for sigma_offset in sigma_offset_vals:
        for option_type in ('call', 'put'):
            count += 1
            if count % 50 == 0:
                print(f"  Progress: {count}/{total}")
            
            # Compute premium across spots
            prem = []
            for s in spots:
                # Unwind value
                if option_type == 'call':
                    unwind = lattice.black_scholes_call(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
                else:
                    unwind = lattice.black_scholes_put(s, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(s, K, T, r, sigma_fair)
                # Continuation using small tree (n_small=15)
                dt = T / 15
                u = np.exp(sigma_spot * np.sqrt(dt))
                d = 1.0 / u
                q = (np.exp(r * dt) - d) / (u - d)
                val_up, _, _ = lattice.binomial_tree_value(
                    14, s * u, K, T - dt, r, sigma_spot, sigma_fair_func,
                    sigma_offset, option_type=option_type)
                val_down, _, _ = lattice.binomial_tree_value(
                    14, s * d, K, T - dt, r, sigma_spot, sigma_fair_func,
                    sigma_offset, option_type=option_type)
                cont = np.exp(-r * dt) * (q * val_up + (1 - q) * val_down)
                prem.append(unwind - cont)
            
            # Find zero crossings (premium changes sign)
            zeros = []
            for i in range(len(spots)-1):
                if prem[i] * prem[i+1] <= 0:
                    x0, x1 = spots[i], spots[i+1]
                    y0, y1 = prem[i], prem[i+1]
                    if abs(y1 - y0) < 1e-12:
                        zero = (x0 + x1) / 2
                    else:
                        zero = x0 - y0 * (x1 - x0) / (y1 - y0)
                    zeros.append(zero)
            
            # Classify boundary type
            num_zeros = len(zeros)
            if num_zeros == 0:
                # No crossing: check sign
                if all(p > 0 for p in prem):
                    boundary_type = "always_exercise"
                    lower_boundary = np.nan
                    upper_boundary = np.nan
                else:
                    boundary_type = "never_exercise"
                    lower_boundary = np.nan
                    upper_boundary = np.nan
            elif num_zeros == 1:
                # One boundary: determine exercise region side
                zero = zeros[0]
                # Check sign beyond zero
                idx_high = np.where(spots > zero)[0][0]
                if prem[idx_high] > 0:
                    # exercise above zero
                    boundary_type = "one_boundary_above"
                    lower_boundary = zero
                    upper_boundary = np.inf
                else:
                    # exercise below zero
                    boundary_type = "one_boundary_below"
                    lower_boundary = -np.inf
                    upper_boundary = zero
            elif num_zeros == 2:
                boundary_type = "two_boundaries"
                lower_boundary = zeros[0]
                upper_boundary = zeros[1]
                # Ensure ordering
                if lower_boundary > upper_boundary:
                    lower_boundary, upper_boundary = upper_boundary, lower_boundary
            else:
                # More than two zeros (unlikely)
                boundary_type = f"multiple_{num_zeros}"
                lower_boundary = zeros[0]
                upper_boundary = zeros[-1]
            
            # Early‑exercise premium at S0=100
            if option_type == 'call':
                euro = lattice.black_scholes_call(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_call(S0, K, T, r, sigma_fair)
            else:
                euro = lattice.black_scholes_put(S0, K, T, r, sigma_fair + sigma_offset) - lattice.black_scholes_put(S0, K, T, r, sigma_fair)
            amer, _, _ = lattice.binomial_tree_value(
                100, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type=option_type)
            early_premium = amer - euro
            
            results.append({
                'sigma_fair': sigma_fair,
                'sigma_offset': sigma_offset,
                'option_type': option_type,
                'num_zeros': num_zeros,
                'boundary_type': boundary_type,
                'lower_boundary': lower_boundary,
                'upper_boundary': upper_boundary,
                'early_exercise_premium': early_premium,
                'american_value': amer,
                'european_value': euro,
            })

# Convert to DataFrame
df = pd.DataFrame(results)
# Save to CSV
csv_path = 'output/two_boundary_results.csv'
df.to_csv(csv_path, index=False)
print(f"\n✅ Results saved to {csv_path}")

# Summary statistics
print("\n=== Summary across all combos ===")
print(f"Total combos: {len(df)}")
print("\nBoundary type distribution:")
print(df['boundary_type'].value_counts())
print("\nNumber of zero crossings distribution:")
print(df['num_zeros'].value_counts().sort_index())

# Show sample of combos with two boundaries
two = df[df['num_zeros'] == 2]
if len(two) > 0:
    print(f"\nFound {len(two)} combos with two boundaries (finite exercise range):")
    print(two[['sigma_fair','sigma_offset','option_type','lower_boundary','upper_boundary']].head(10))
else:
    print("\nNo combos with two boundaries found.")

# For each sigma_fair, count how many sigma_offset produce two boundaries
if len(two) > 0:
    print("\nTwo‑boundary combos per σ_fair:")
    for sf in sigma_fair_vals:
        subset = two[abs(two['sigma_fair'] - sf) < 1e-6]
        if len(subset) > 0:
            call_cnt = len(subset[subset['option_type']=='call'])
            put_cnt = len(subset[subset['option_type']=='put'])
            print(f"σ_fair={sf:.2f}: call={call_cnt}, put={put_cnt}")

# Also compute for each combo whether call and put have same boundary type
print("\n=== Call vs Put boundary type agreement ===")
df_pivot = df.pivot_table(index=['sigma_fair','sigma_offset'],
                          columns='option_type',
                          values='boundary_type',
                          aggfunc='first')
df_pivot['same'] = df_pivot['call'] == df_pivot['put']
print("Call and Put have same boundary type?")
print(df_pivot['same'].value_counts())

# Save pivot to CSV
df_pivot.to_csv('output/boundary_type_pivot.csv')
print("\n✅ Pivot table saved to output/boundary_type_pivot.csv")