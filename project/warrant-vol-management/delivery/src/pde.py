"""
PDE (HJB) method for pricing the arbitrage derivative using finite differences.
Implicit Euler with explicit constraint enforcement (penalty method).
"""
import numpy as np
from scipy.stats import norm
from scipy.sparse import diags, csr_matrix
from scipy.sparse.linalg import spsolve
from typing import Callable


def black_scholes_call(spot: float, strike: float, time_to_expiry: float,
                       risk_free_rate: float, volatility: float) -> float:
    """European call option price via Black-Scholes."""
    if time_to_expiry <= 0.0:
        return max(spot - strike, 0.0)
    d1 = (np.log(spot / strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) \
         / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)
    return spot * norm.cdf(d1) - strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)


def pde_value(
    S_min: float,
    S_max: float,
    n_S: int,
    n_t: int,
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma_spot: float,
    sigma_fair_func: Callable[[float], float],
    sigma_offset: float,
    method: str = 'implicit',
    omega: float = 1.2,
    max_iter: int = 100,
    tol: float = 1e-8,
) -> tuple[float, float, float]:
    """
    Solve HJB PDE via finite differences with early exercise constraint.
    
    Parameters
    ----------
    S_min, S_max : float
        Boundaries of stock price grid.
    n_S : int
        Number of spatial grid points (including boundaries).
    n_t : int
        Number of time steps.
    S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset : same as lattice.
    method : str, optional
        'explicit', 'implicit', or 'cn' (Crank-Nicolson). Default 'implicit'.
    omega : float
        Relaxation parameter for PSOR (1 < omega < 2).
    max_iter : int
        Maximum PSOR iterations per time step.
    tol : float
        Convergence tolerance for PSOR.
    
    Returns
    -------
    value : float
        Derivative value at S0 (max of exercise and continuation values).
    exercise_value : float
        Immediate unwind value at S0, time 0.
    continuation_value : float
        Value of holding the derivative without unwinding now.
    """
    # Grid setup
    S_grid = np.linspace(S_min, S_max, n_S)
    dS = S_grid[1] - S_grid[0]
    dt = T / n_t
    
    # Precompute unwind values for each (S, t)
    unwind = np.zeros((n_S, n_t + 1))
    for i, S in enumerate(S_grid):
        for j in range(n_t + 1):
            t = j * dt
            time_to_expiry = T - t
            vol_low = sigma_fair_func(S)
            vol_high = vol_low + sigma_offset
            price_low = black_scholes_call(S, K, time_to_expiry, r, vol_low)
            price_high = black_scholes_call(S, K, time_to_expiry, r, vol_high)
            unwind[i, j] = price_high - price_low
    
    # Initialize value grid at maturity
    V = unwind[:, -1].copy()
    # Store history
    V_history = np.zeros((n_S, n_t + 1))
    V_history[:, -1] = V
    
    # Finite difference coefficients
    # For each interior grid point i (1 <= i <= n_S-2)
    # We'll construct tridiagonal matrix A and rhs vector b
    # Implicit Euler: (I - dt * L) V^{n} = V^{n+1}
    # where L is spatial discretization of Black-Scholes operator:
    # L V = 0.5 * sigma_spot^2 * S_i^2 * (V_{i+1} - 2V_i + V_{i-1})/dS^2
    #        + r * S_i * (V_{i+1} - V_{i-1})/(2 dS) - r * V_i
    
    # Precompute coefficients for interior points
    alpha = np.zeros(n_S)  # subdiagonal coefficient (connects row i to i-1)
    beta = np.zeros(n_S)   # diagonal coefficient
    gamma = np.zeros(n_S)  # superdiagonal coefficient (connects row i to i+1)
    for i in range(1, n_S - 1):
        S = S_grid[i]
        alpha[i] = 0.5 * sigma_spot ** 2 * S ** 2 / (dS ** 2) - r * S / (2 * dS)
        beta[i] = -sigma_spot ** 2 * S ** 2 / (dS ** 2) - r
        gamma[i] = 0.5 * sigma_spot ** 2 * S ** 2 / (dS ** 2) + r * S / (2 * dS)
    
    # Boundary conditions: V = 0 at S_min and S_max (both calls go to zero for S->0 and S->∞)
    # Implement by setting rows for i=0 and i=n_S-1 to identity.
    alpha[0] = 0.0
    beta[0] = 1.0
    gamma[0] = 0.0
    alpha[-1] = 0.0
    beta[-1] = 1.0
    gamma[-1] = 0.0
    
    # Construct tridiagonal matrix for implicit Euler: M = I - dt * L
    # L is represented by subdiagonal alpha, diagonal beta, superdiagonal gamma
    # So M's diagonal = 1 - dt * beta, subdiagonal = -dt * alpha, superdiagonal = -dt * gamma
    # Except at boundaries where we set identity.
    diag = 1 - dt * beta
    sub = -dt * alpha[1:]   # subdiagonal elements for rows 1..n_S-1 (length n_S-1)
    sup = -dt * gamma[:-1]  # superdiagonal elements for rows 0..n_S-2 (length n_S-1)
    
    # Ensure boundary rows are identity (already via beta=1, alpha=0, gamma=0)
    # Build sparse matrix
    M = diags([sub, diag, sup], offsets=[-1, 0, 1], format='csr')
    
    # For explicit constraint enforcement, we'll solve M V_new = V_old, then project.
    # Actually we need to solve linear complementarity problem.
    # We'll use Projected SOR (PSOR) iteration.
    
    # Variables to store exercise and continuation values at time 0
    exercise_value = None
    continuation_value = None

    # Time stepping backward
    exercise_boundary = np.full(n_t + 1, np.inf)
    # At maturity, exercise region where unwind > small threshold
    meaningful = unwind[:, -1] > 1e-3
    if np.any(meaningful):
        exercise_boundary[-1] = np.min(S_grid[meaningful])

    for step in range(n_t - 1, -1, -1):
        V_old = V.copy()
        phi = unwind[:, step]  # exercise value at this time
        
        # For step 0 (initial time), compute continuation value without constraint
        if step == 0:
            # Solve linear system for continuation values (without constraint)
            continuation_grid = spsolve(M, V_old)
            continuation_value = np.interp(S0, S_grid, continuation_grid)
            exercise_value = np.interp(S0, S_grid, phi)
        
        # Projected SOR iteration using tridiagonal coefficients
        V_new = V_old.copy()  # initial guess
        for it in range(max_iter):
            V_prev = V_new.copy()
            # Gauss-Seidel step with relaxation, using sub, diag, sup arrays
            for i in range(n_S):
                # Compute sum of contributions from other rows
                sigma = 0.0
                if i > 0:
                    sigma += sub[i-1] * V_new[i-1]   # sub[i-1] connects row i to i-1
                if i < n_S - 1:
                    sigma += sup[i] * V_prev[i+1]    # sup[i] connects row i to i+1 (use old value)
                # Solve for V_new[i]
                v = (V_old[i] - sigma) / diag[i]
                # Projection step: enforce constraint V >= phi
                v = max(v, phi[i])
                # Relaxation
                V_new[i] = V_prev[i] + omega * (v - V_prev[i])
            # Check convergence
            if np.max(np.abs(V_new - V_prev)) < tol:
                break
        
        # Update V
        V = V_new
        V_history[:, step] = V
        
        # Determine exercise boundary: smallest S where V == phi (exercise region)
        # Actually, exercise region is where constraint is binding and unwind value is meaningful.
        meaningful = phi > 1e-3
        binding = np.abs(V - phi) < 1e-6
        exercise = meaningful & binding
        if np.any(exercise):
            exercise_boundary[step] = np.min(S_grid[exercise])

    # Interpolate to S0
    value = np.interp(S0, S_grid, V)

    return value, exercise_value, continuation_value


def test_pde():
    """Simple test case."""
    S_min = 1.0
    S_max = 300.0
    n_S = 200
    n_t = 100
    S0 = 100.0
    K = 100.0
    T = 1.0
    r = 0.05
    sigma_spot = 0.2
    sigma_fair_func = lambda s: 0.2
    sigma_offset = 0.1
    
    val, exercise_value, continuation_value = pde_value(
        S_min, S_max, n_S, n_t, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset
    )
    print(f"PDE value: {val}")
    print(f"Exercise value: {exercise_value}")
    print(f"Continuation value: {continuation_value}")
    print(f"Exercise premium (exercise - continuation): {exercise_value - continuation_value}")
    return val


if __name__ == "__main__":
    test_pde()