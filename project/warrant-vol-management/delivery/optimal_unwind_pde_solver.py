import numpy as np
import scipy.linalg as linalg
from scipy.stats import norm

# ====================== BLACK-SCHOLES HELPERS ======================
def black_scholes_call(S, K, sigma, T=1.0, r=0.0, q=0.0):
    if T <= 0: return np.maximum(S - K, 0.0)
    if sigma <= 0: return np.maximum(S * np.exp(-q * T) - K * np.exp(-r * T), 0.0)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def black_scholes_put(S, K, sigma, T=1.0, r=0.0, q=0.0):
    if T <= 0: return np.maximum(K - S, 0.0)
    if sigma <= 0: return np.maximum(K * np.exp(-r * T) - S * np.exp(-q * T), 0.0)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

def bs_spread(S, K, vol_high, vol_base, option_type, T, r, q):
    if option_type.lower() == 'call':
        return black_scholes_call(S, K, vol_high, T, r, q) - black_scholes_call(S, K, vol_base, T, r, q)
    else:
        return black_scholes_put(S, K, vol_high, T, r, q) - black_scholes_put(S, K, vol_base, T, r, q)

# ====================== HJB PDE SOLVER ======================
def pde_optimal_unwind(K, vol_high, vol_base, sigma_spot, option_type='call', T=1.0, r=0.0, q=0.0, S0=100.0, M=300, N=1500):
    """
    Solves the HJB LCP for optimal spread unwind using an Implicit Finite Difference Method.
    Returns: optimal_pnl, expected_spread, boundary_S_list, boundary_ttm_list
    """
    S_max = K * 3.0
    dS = S_max / M
    dt = T / N
    S = np.linspace(0, S_max, M + 1)
    
    # Terminal condition (at maturity, TTM = 0, time value vanishes)
    # Using a tiny epsilon for T because BS implied vol formulas divide by sqrt(T)
    U = np.array([bs_spread(s, K, vol_high, vol_base, option_type, 1e-6, r, q) for s in S])
    
    # Implicit FDM matrix setup (dU/dtau = 0.5*sigma^2*S^2*U_SS + (r-q)*S*U_S - r*U)
    j = np.arange(1, M)
    alpha = 0.5 * dt * sigma_spot**2 * j**2
    beta  = 0.5 * dt * (r - q) * j
    
    lower_diag = -alpha + beta
    main_diag  = 1.0 + 2*alpha + r*dt
    upper_diag = -alpha - beta
    
    A = np.zeros((3, M - 1))
    A[0, 1:] = upper_diag[:-1]  
    A[1, :]  = main_diag        
    A[2, :-1] = lower_diag[1:]  

    boundary_ttm = []
    boundary_S_min = []
    boundary_S_max = []

    # Step backward in time (forward in Time-to-Maturity tau)
    for n in range(1, N + 1):
        tau = n * dt
        obstacle = np.array([bs_spread(s, K, vol_high, vol_base, option_type, tau, r, q) for s in S])
        
        B = U[1:M].copy()
        
        # Dirichlet boundary conditions (Assuming spread -> 0 as S->0 and S->inf)
        # B[0] -= lower_diag[0] * obstacle[0]
        # B[-1] -= upper_diag[-1] * obstacle[-1]
        
        # Solve unconstrained continuation value
        U_unconstrained = np.zeros_like(U)
        U_unconstrained[1:M] = linalg.solve_banded((1, 1), A, B)
        U_unconstrained[0] = obstacle[0]
        U_unconstrained[-1] = obstacle[-1]
        
        # Apply American/Early-Exercise Constraint
        U = np.maximum(U_unconstrained, obstacle)
        
        # Extract exercise boundary (where obstacle == U)
        exercise_idx = np.where(obstacle >= U_unconstrained - 1e-7)[0]
        if len(exercise_idx) > 0:
            # The exercise region might be two-sided for a spread. We track the bounds.
            valid_S = S[exercise_idx]
            # Filter out S=0 and S=S_max edge artifacts
            valid_S = valid_S[(valid_S > dS) & (valid_S < S_max - dS)]
            if len(valid_S) > 0:
                boundary_S_min.append(np.min(valid_S))
                boundary_S_max.append(np.max(valid_S))
            else:
                boundary_S_min.append(np.nan)
                boundary_S_max.append(np.nan)
        else:
            boundary_S_min.append(np.nan)
            boundary_S_max.append(np.nan)
        
        boundary_ttm.append(tau)
        
    optimal_expected_spread = np.interp(S0, S, U)
    debit = bs_spread(S0, K, vol_high, vol_base, option_type, T, r, q)
    optimal_pnl = optimal_expected_spread - debit
    
    return optimal_pnl, optimal_expected_spread, np.array(boundary_S_min), np.array(boundary_S_max), np.array(boundary_ttm)