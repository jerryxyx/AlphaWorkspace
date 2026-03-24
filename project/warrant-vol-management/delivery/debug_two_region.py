#!/usr/bin/env python3
"""
Debug a two_region case.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np

K=100.0; S0=100.0; T=1.0; r=0.05; sigma_fair=0.20; sigma_offset=0.02; sigma_spot=sigma_fair
def sigma_fair_func(spot): return sigma_fair

n=50
amer, boundary, ex_flags = lattice.binomial_tree_value(
    n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')

# Examine step n-1 (near expiry)
step = n-1
dt = T / n
u = np.exp(sigma_spot * np.sqrt(dt))
d = 1.0 / u
spots = S0 * (u ** np.arange(step, -1, -1)) * (d ** np.arange(0, step+1))
ex = ex_flags[step]
print(f"Step {step} (t={step*dt:.3f}), spots count={len(spots)}")
print("Spots (descending):", spots.round(2))
print("Exercise flags:", ex)
print("Boundary[step] =", boundary[step])
# Print each spot with flag
for i in range(len(spots)):
    print(f"  {spots[i]:6.2f}: {'EX' if ex[i] else '  '}")
# Check regions
changes = np.diff(ex.astype(int))
starts = np.where(changes == 1)[0] + 1
ends = np.where(changes == -1)[0]
if ex[0]: starts = np.insert(starts, 0, 0)
if ex[-1]: ends = np.append(ends, len(ex)-1)
print("Starts:", starts, "Ends:", ends)
regions = []
for s,e in zip(starts, ends):
    if s <= e:
        regions.append((spots[e], spots[s]))
print("Regions (lower, upper):", regions)

# Also compute premium for a few spots
print("\nPremium (unwind - continuation) for spots 50,100,150:")
for s in [50,100,150]:
    unwind = lattice.black_scholes_call(s, K, T, r, sigma_fair+sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
    dt_small = T/10
    u_small = np.exp(sigma_spot*np.sqrt(dt_small))
    d_small = 1/u_small
    q_small = (np.exp(r*dt_small)-d_small)/(u_small-d_small)
    val_up,_,_ = lattice.binomial_tree_value(9, s*u_small, K, T-dt_small, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    val_down,_,_ = lattice.binomial_tree_value(9, s*d_small, K, T-dt_small, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
    cont = np.exp(-r*dt_small)*(q_small*val_up + (1-q_small)*val_down)
    prem = unwind - cont
    print(f"  spot {s}: unwind={unwind:.4f}, cont={cont:.4f}, prem={prem:.4f}")