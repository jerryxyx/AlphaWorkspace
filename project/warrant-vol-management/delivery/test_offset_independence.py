#!/usr/bin/env python3
"""
Test whether zero crossings of premium are independent of sigma_offset.
"""
import sys
sys.path.insert(0, 'src')
import lattice
import numpy as np

K=100.0; S0=100.0; T=1.0; r=0.05; sigma_fair=0.3; sigma_spot=sigma_fair
def sigma_fair_func(spot): return sigma_fair

spots = np.linspace(50,150,101)
for sigma_offset in [0.0, 0.05, 0.1]:
    prem = []
    for s in spots:
        unwind = lattice.black_scholes_call(s, K, T, r, sigma_fair+sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
        dt = T/15
        u=np.exp(sigma_spot*np.sqrt(dt)); d=1/u; q=(np.exp(r*dt)-d)/(u-d)
        val_up,_,_ = lattice.binomial_tree_value(14, s*u, K, T-dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
        val_down,_,_ = lattice.binomial_tree_value(14, s*d, K, T-dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
        cont = np.exp(-r*dt)*(q*val_up + (1-q)*val_down)
        prem.append(unwind - cont)
    # Find zero crossings
    zeros=[]
    for i in range(len(spots)-1):
        if prem[i]*prem[i+1] <= 0:
            x0,x1=spots[i],spots[i+1]; y0,y1=prem[i],prem[i+1]
            if abs(y1-y0)<1e-12: zero=(x0+x1)/2
            else: zero=x0 - y0*(x1-x0)/(y1-y0)
            zeros.append(zero)
    print(f"σ_offset={sigma_offset:.2f}: zeros={zeros}, premium range [{min(prem):.3f},{max(prem):.3f}]")
    # Also compute at a few spots
    for s in [70,100,130]:
        unwind = lattice.black_scholes_call(s, K, T, r, sigma_fair+sigma_offset) - lattice.black_scholes_call(s, K, T, r, sigma_fair)
        val_up,_,_ = lattice.binomial_tree_value(14, s*u, K, T-dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
        val_down,_,_ = lattice.binomial_tree_value(14, s*d, K, T-dt, r, sigma_spot, sigma_fair_func, sigma_offset, option_type='call')
        cont = np.exp(-r*dt)*(q*val_up + (1-q)*val_down)
        print(f"  spot {s}: unwind={unwind:.4f}, cont={cont:.4f}, prem={unwind-cont:.4f}")