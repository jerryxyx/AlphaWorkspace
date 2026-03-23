"""
Monte Carlo Least Squares Method (LSM) for pricing the arbitrage derivative.
"""
import numpy as np
from scipy.stats import norm
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


def lsm_value(
    n_paths: int,
    n_steps: int,
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma_spot: float,
    sigma_fair_func: Callable[[float], float],
    sigma_offset: float,
    basis_funcs: list = None,
) -> tuple[float, np.ndarray]:
    """
    LSM valuation of the arbitrage derivative.
    
    Parameters
    ----------
    n_paths : int
        Number of simulated paths.
    n_steps : int
        Number of exercise opportunities (including maturity).
    S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset : same as lattice.
    basis_funcs : list of callable, optional
        Basis functions for regression, each mapping spot to float.
        Default: [lambda x: 1, lambda x: x, lambda x: x**2].
    
    Returns
    -------
    value : float
        Derivative value at time 0.
    exercise_boundary : np.ndarray shape (n_steps,)
        For each time step, the approximate spot level above which exercise is optimal,
        estimated from in-the-money paths.
    """
    if basis_funcs is None:
        basis_funcs = [lambda x: np.ones_like(x), lambda x: x, lambda x: x ** 2]
    
    dt = T / (n_steps - 1) if n_steps > 1 else T
    # Simulate risk-neutral GBM paths (antithetic variates for variance reduction)
    # We'll generate normal increments
    np.random.seed(12345)  # for reproducibility
    Z = np.random.randn(n_paths // 2, n_steps - 1)
    Z = np.vstack([Z, -Z])  # antithetic
    if Z.shape[0] < n_paths:
        # add extra if odd
        extra = np.random.randn(n_paths - Z.shape[0], n_steps - 1)
        Z = np.vstack([Z, extra])
    
    # Initialize spot paths matrix: (n_paths, n_steps)
    S = np.zeros((n_paths, n_steps))
    S[:, 0] = S0
    for t in range(1, n_steps):
        S[:, t] = S[:, t - 1] * np.exp((r - 0.5 * sigma_spot ** 2) * dt + sigma_spot * np.sqrt(dt) * Z[:, t - 1])
    
    # Compute immediate exercise value at each time step
    exercise_value = np.zeros_like(S)
    for t in range(n_steps):
        time_to_expiry = T - t * dt
        for p in range(n_paths):
            spot = S[p, t]
            vol_low = sigma_fair_func(spot)
            vol_high = vol_low + sigma_offset
            price_low = black_scholes_call(spot, K, time_to_expiry, r, vol_low)
            price_high = black_scholes_call(spot, K, time_to_expiry, r, vol_high)
            exercise_value[p, t] = price_high - price_low
    
    # Initialize cashflow matrix (value if exercised at each time)
    cashflow = np.zeros_like(S)
    cashflow[:, -1] = exercise_value[:, -1]  # at maturity
    
    # Backward induction
    for t in range(n_steps - 2, -1, -1):
        # In-the-money paths at time t (exercise value > 0)
        itm = exercise_value[:, t] > 0
        if np.sum(itm) == 0:
            # No exercise opportunity
            cashflow[:, t] = cashflow[:, t + 1] * np.exp(-r * dt)
            continue
        # Design matrix for regression
        X = np.column_stack([func(S[itm, t]) for func in basis_funcs])  # shape (n_itm, n_basis)
        # Continuation value discounted from next step
        Y = cashflow[itm, t + 1] * np.exp(-r * dt)
        # Least squares regression
        beta = np.linalg.lstsq(X, Y, rcond=None)[0]
        continuation_estimate = X @ beta
        # Exercise decision: exercise if exercise value >= continuation estimate
        exercise = exercise_value[itm, t] >= continuation_estimate
        # Update cashflows
        cashflow[itm, t] = np.where(exercise,
                                     exercise_value[itm, t],
                                     cashflow[itm, t + 1] * np.exp(-r * dt))
        # For out-of-the-money paths, continue
        cashflow[~itm, t] = cashflow[~itm, t + 1] * np.exp(-r * dt)
    
    # Discount back to time 0
    value = np.mean(cashflow[:, 0])
    
    # Estimate exercise boundary: for each time step, compute average spot where exercise occurred
    # For simplicity, we'll compute the minimum spot among exercised paths.
    exercise_boundary = np.full(n_steps, np.inf)
    for t in range(n_steps):
        exercised = cashflow[:, t] == exercise_value[:, t]  # paths that exercised at t
        if np.any(exercised):
            exercise_boundary[t] = np.min(S[exercised, t])
    
    return value, exercise_boundary


def test_lsm():
    """Simple test case."""
    n_paths = 10000
    n_steps = 50
    S0 = 100.0
    K = 100.0
    T = 1.0
    r = 0.05
    sigma_spot = 0.2
    sigma_fair_func = lambda s: 0.2
    sigma_offset = 0.1
    
    val, boundary = lsm_value(
        n_paths, n_steps, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset
    )
    print(f"LSM value: {val}")
    print(f"Boundary (first 5 steps): {boundary[:5]}")
    return val


if __name__ == "__main__":
    test_lsm()