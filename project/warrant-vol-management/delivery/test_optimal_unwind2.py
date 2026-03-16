"""
VOL-SPREAD ARBITRAGE RESEARCH SUITE
===================================

Features
--------
1. Spot scenario PnL
2. Expected PnL validation
3. LSM optimal stopping
4. 2-factor HJB PDE solver
5. Diagnostic plots

State variables:
    Spot S
    Volatility spread Δσ

Author: Quant research framework
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, lognorm
from scipy.integrate import quad


# ================================================================
# BLACK-SCHOLES (vectorized)
# ================================================================

def bs_call(S,K,sigma,T,r=0):

    S=np.asarray(S)

    if T<=0:
        return np.maximum(S-K,0)

    d1=(np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    d2=d1-sigma*np.sqrt(T)

    return S*norm.cdf(d1)-K*np.exp(-r*T)*norm.cdf(d2)


# ================================================================
# VOL-SPREAD PAYOFF
# ================================================================

def spread_price(S,K,vol_base,vol_spread,T):

    vol_high=vol_base+vol_spread

    return bs_call(S,K,vol_high,T)-bs_call(S,K,vol_base,T)


def pnl(S,S0,K,vol_base,vol_spread,T):

    debit=spread_price(S0,K,vol_base,vol_spread,T)

    return spread_price(S,K,vol_base,vol_spread,T)-debit


# ================================================================
# EXPECTED PNL METHODS
# ================================================================

def expected_theoretical(K,vol_base,vol_spread,sigma_spot,S0,T):

    sig_h=np.sqrt((vol_base+vol_spread)**2+sigma_spot**2)
    sig_b=np.sqrt(vol_base**2+sigma_spot**2)

    e_high=bs_call(S0,K,sig_h,T)
    e_base=bs_call(S0,K,sig_b,T)

    debit=spread_price(S0,K,vol_base,vol_spread,T)

    return e_high-e_base-debit


def expected_numeric(K,vol_base,vol_spread,sigma_spot,S0,T):

    def integrand(S):

        pdf=lognorm.pdf(S,s=sigma_spot,scale=S0*np.exp(-0.5*sigma_spot**2))

        return pnl(S,S0,K,vol_base,vol_spread,T)*pdf

    val,_=quad(integrand,0,500)

    return val


def expected_mc(K,vol_base,vol_spread,sigma_spot,S0,T,n=200000):

    Z=np.random.randn(n)

    S=S0*np.exp(-0.5*sigma_spot**2+sigma_spot*Z)

    return np.mean(pnl(S,S0,K,vol_base,vol_spread,T))


# ================================================================
# SPOT PATH SIMULATION
# ================================================================

def simulate_spot(S0,sigma,T,steps,paths):

    dt=T/steps

    S=np.zeros((paths,steps+1))
    S[:,0]=S0

    for i in range(1,steps+1):

        Z=np.random.randn(paths)

        S[:,i]=S[:,i-1]*np.exp(-0.5*sigma**2*dt+sigma*np.sqrt(dt)*Z)

    return S


# ================================================================
# LSM OPTIMAL STOPPING (spot only)
# ================================================================

def lsm_solver(K,vol_base,vol_spread,sigma_spot,S0,T,
               paths=15000,steps=40):

    dt=T/steps

    S=simulate_spot(S0,sigma_spot,T,steps,paths)

    V=np.zeros(paths)

    boundary=[]

    for step in reversed(range(steps)):

        tau=(steps-step)*dt

        spot=S[:,step]

        exercise=spread_price(spot,K,vol_base,vol_spread,tau)

        X=spot/K

        basis=np.column_stack([np.ones(paths),X,X**2])

        coef=np.linalg.lstsq(basis,V,rcond=None)[0]

        continuation=basis@coef

        ex=exercise>continuation

        if np.any(ex):
            boundary.append(np.percentile(spot[ex],20))
        else:
            boundary.append(np.nan)

        V[ex]=exercise[ex]

    debit=spread_price(S0,K,vol_base,vol_spread,T)

    return np.mean(V)-debit,boundary


# ================================================================
# 2-FACTOR HJB PDE SOLVER
# ================================================================

def hjb_2factor_solver(
        K,
        vol_base,
        S0=100,
        Smax=200,
        dS=80,
        vol_spread_max=0.2,
        dv=40,
        T=1,
        Nt=120,
        sigma_spot=0.2,
        kappa=3,
        theta=0.05,
        eta=0.15):

    S=np.linspace(1,Smax,dS)
    V=np.linspace(0,vol_spread_max,dv)

    dt=T/Nt

    value=np.zeros((dS,dv))

    boundary=[]

    for n in range(Nt):

        tau=T-n*dt

        Phi=np.zeros_like(value)

        for i in range(dS):
            for j in range(dv):

                Phi[i,j]=spread_price(
                    S[i],
                    K,
                    vol_base,
                    V[j],
                    tau
                )

        new_val=value.copy()

        for i in range(1,dS-1):
            for j in range(1,dv-1):

                dS1=(value[i+1,j]-value[i-1,j])/(2*(S[1]-S[0]))
                dS2=(value[i+1,j]-2*value[i,j]+value[i-1,j])/(S[1]-S[0])**2

                dv1=(value[i,j+1]-value[i,j-1])/(2*(V[1]-V[0]))
                dv2=(value[i,j+1]-2*value[i,j]+value[i,j-1])/(V[1]-V[0])**2

                drift_spot=0.5*sigma_spot**2*S[i]**2*dS2
                drift_vol=kappa*(theta-V[j])*dv1+0.5*eta**2*dv2

                new_val[i,j]=value[i,j]+dt*(drift_spot+drift_vol)

        value=np.maximum(new_val,Phi)

        boundary_slice=[]

        for j in range(dv):

            ex=value[:,j]<=Phi[:,j]+1e-8

            if np.any(ex):
                boundary_slice.append(S[ex].max())
            else:
                boundary_slice.append(np.nan)

        boundary.append(boundary_slice)

    return S,V,value,boundary


# ================================================================
# TESTS
# ================================================================

def test_spot_scenarios():

    print("\nSPOT PNL SCENARIOS")

    S0=100
    T=1
    vol_base=0.20
    vol_spread=0.05

    strikes=[80,90,100,110,120]

    S=np.linspace(50,150,400)

    plt.figure(figsize=(8,6))

    for K in strikes:

        plt.plot(S,pnl(S,S0,K,vol_base,vol_spread,T),label=f"K={K}")

    plt.axhline(0,color="black")

    plt.title("PnL vs Spot")

    plt.legend()

    plt.show()


def test_expected():

    print("\nEXPECTED PNL VALIDATION")

    S0=100
    sigma=0.2
    vol_base=0.20
    vol_spread=0.05
    T=1

    strikes=[80,90,100,110,120]

    for K in strikes:

        theo=expected_theoretical(K,vol_base,vol_spread,sigma,S0,T)
        num=expected_numeric(K,vol_base,vol_spread,sigma,S0,T)
        mc=expected_mc(K,vol_base,vol_spread,sigma,S0,T)

        print(f"K={K} theo={theo:.4f} num={num:.4f} mc={mc:.4f}")


def test_lsm():

    print("\nLSM OPTIMAL BOUNDARY")

    S0=100
    sigma=0.2
    vol_base=0.20
    vol_spread=0.05
    T=1
    K=100

    pnl,boundary=lsm_solver(K,vol_base,vol_spread,sigma,S0,T)

    plt.plot(boundary)

    plt.title("LSM optimal boundary")

    plt.show()


def test_hjb():

    print("\n2-FACTOR HJB SOLVER")

    K=100
    vol_base=0.20

    S,V,val,boundary=hjb_2factor_solver(K,vol_base)

    boundary=np.array(boundary)

    plt.imshow(boundary.T,
               origin="lower",
               aspect="auto")

    plt.colorbar()

    plt.title("Unwind boundary vs vol spread")

    plt.xlabel("Time step")

    plt.ylabel("Vol spread index")

    plt.show()

def compare_lsm_pde_boundary(
        K=100,
        S0=100,
        sigma_spot=0.20,
        vol_base=0.20,
        vol_high=0.25,
        T=1.0):

    vol_spread = vol_high - vol_base

    print("\n===== USER PARAMETERS =====")
    print(f"K={K}")
    print(f"S0={S0}")
    print(f"sigma_spot={sigma_spot}")
    print(f"vol_base={vol_base}")
    print(f"vol_high={vol_high}")
    print(f"vol_spread={vol_spread}")
    print(f"T={T}")

    # ---------------- LSM ----------------
    lsm_pnl, lsm_boundary = lsm_solver(
        K,
        vol_base,
        vol_spread,
        sigma_spot,
        S0,
        T
    )

    lsm_boundary = np.array(lsm_boundary)
    lsm_boundary = lsm_boundary[::-1]

    time_lsm = np.linspace(0, T, len(lsm_boundary))

    # ---------------- PDE ----------------
    S, V, val, pde_surface = hjb_2factor_solver(
        K,
        vol_base,
        S0=S0,
        sigma_spot=sigma_spot,
        T=T
    )

    pde_surface = np.array(pde_surface)

    # choose vol_spread slice closest to initial spread
    vol_grid = V
    idx = np.argmin(np.abs(vol_grid - vol_spread))

    pde_boundary = pde_surface[:, idx]

    time_pde = np.linspace(0, T, len(pde_boundary))

    # ---------------- Plot ----------------

    plt.figure(figsize=(9,6))

    plt.plot(
        time_lsm,
        lsm_boundary,
        label="LSM boundary (spot-only model)",
        linewidth=2
    )

    plt.plot(
        time_pde,
        pde_boundary,
        label="2-factor PDE boundary",
        linewidth=2
    )

    plt.axhline(K, linestyle="--", color="gray", label="Strike")

    plt.xlabel("Time to maturity")
    plt.ylabel("Optimal unwind spot S*")

    plt.title(
        f"Optimal Unwind Boundary Comparison\n"
        f"K={K}, S0={S0}, σ_spot={sigma_spot}, "
        f"vol_base={vol_base}, vol_high={vol_high}"
    )

    plt.legend()
    plt.grid()

    plt.show()

    print("\nLSM expected optimal PnL:", lsm_pnl)

def test_lsm_hjb():

    print("\nVOL SPREAD ARBITRAGE RESEARCH")

    K = float(input("Strike K (default 100): ") or 100)
    S0 = float(input("Spot S0 (default 100): ") or 100)
    sigma_spot = float(input("Spot vol sigma_spot (default 0.2): ") or 0.2)
    vol_base = float(input("Base implied vol (default 0.20): ") or 0.20)
    vol_high = float(input("High implied vol (default 0.25): ") or 0.25)
    T = float(input("Maturity T years (default 1): ") or 1)

    compare_lsm_pde_boundary(
        K=K,
        S0=S0,
        sigma_spot=sigma_spot,
        vol_base=vol_base,
        vol_high=vol_high,
        T=T
    )

# ================================================================
# MAIN
# ================================================================

if __name__=="__main__":

    test_spot_scenarios()

    test_expected()

    test_lsm()
    test_lsm_hjb()
    test_hjb()