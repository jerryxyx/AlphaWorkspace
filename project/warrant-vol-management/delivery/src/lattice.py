"""
Binomial tree lattice method for pricing the arbitrage derivative.

The derivative is long high-vol option (vol = sigma_fair(spot) + sigma_offset)
and short low-vol option (vol = sigma_fair(spot)). Can be unwound anytime.
"""
import numpy as np
from scipy.stats import norm


def black_scholes_call(spot: float, strike: float, time_to_expiry: float,
                       risk_free_rate: float, volatility: float) -> float:
    """
    European call option price via Black-Scholes formula.
    
    Parameters
    ----------
    spot : float
        Current stock price.
    strike : float
        Strike price.
    time_to_expiry : float
        Time to expiry in years.
    risk_free_rate : float
        Continuous risk-free rate.
    volatility : float
        Annualized volatility.
    
    Returns
    -------
    float
        Call price.
    """
    if time_to_expiry <= 0.0:
        return max(spot - strike, 0.0)
    d1 = (np.log(spot / strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) \
         / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)
    return spot * norm.cdf(d1) - strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)


def black_scholes_put(spot: float, strike: float, time_to_expiry: float,
                      risk_free_rate: float, volatility: float) -> float:
    """
    European put option price via Black-Scholes formula.
    
    Parameters
    ----------
    spot : float
        Current stock price.
    strike : float
        Strike price.
    time_to_expiry : float
        Time to expiry in years.
    risk_free_rate : float
        Continuous risk-free rate.
    volatility : float
        Annualized volatility.
    
    Returns
    -------
    float
        Put price.
    """
    if time_to_expiry <= 0.0:
        return max(strike - spot, 0.0)
    d1 = (np.log(spot / strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) \
         / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)
    return strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - spot * norm.cdf(-d1)


def binomial_tree_value(
    n: int,
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma_spot: float,
    sigma_fair_func,
    sigma_offset: float,
    option_type: str = 'call',
) -> tuple[float, float, float]:
    """
    Binomial tree valuation of the arbitrage derivative.
    
    Parameters
    ----------
    n : int
        Number of time steps (height of the tree).
    S0 : float
        Initial stock price.
    K : float
        Strike price.
    T : float
        Time to expiry in years.
    r : float
        Risk-free rate (drift of spot).
    sigma_spot : float
        Diffusion term of spot GBM (true volatility).
    sigma_fair_func : callable (float -> float)
        Function mapping spot to fair implied volatility.
    sigma_offset : float
        Constant margin added to fair vol for the high-vol option.
    option_type : str, optional
        'call' for call spreads, 'put' for put spreads (default 'call').
    
    Returns
    -------
    value : float
        Derivative value at time 0 (max of exercise and continuation values).
    exercise_value : float
        Immediate unwind value at time 0.
    continuation_value : float
        Risk‑neutral expectation of holding the derivative without unwinding now.
    """
    # Validate option_type
    if option_type not in ('call', 'put'):
        raise ValueError("option_type must be 'call' or 'put'")
    
    # Choose pricing function
    if option_type == 'call':
        price_func = black_scholes_call
    else:
        price_func = black_scholes_put
    
    # CRR parameters
    dt = T / n
    u = np.exp(sigma_spot * np.sqrt(dt))  # up factor
    d = 1.0 / u                           # down factor
    q = (np.exp(r * dt) - d) / (u - d)    # risk-neutral up probability
    
    # Precompute spot grid for each node (time step i, state j)
    # spot[i][j] = S0 * u^(j) * d^(i-j) for j = 0..i
    spot_grid = []
    for i in range(n + 1):
        spots = S0 * (u ** np.arange(i, -1, -1)) * (d ** np.arange(0, i + 1))
        spot_grid.append(spots)
    
    # Initialize value grid (backward induction)
    value_grid = [None] * (n + 1)
    
    # At maturity (time step n)
    spots_n = spot_grid[n]
    # Unwind value = BS_high - BS_low
    unwind_values = np.zeros_like(spots_n)
    for idx, spot in enumerate(spots_n):
        vol_low = sigma_fair_func(spot)
        vol_high = vol_low + sigma_offset
        price_low = price_func(spot, K, 0.0, r, vol_low)
        price_high = price_func(spot, K, 0.0, r, vol_high)
        unwind_values[idx] = price_high - price_low
    # At maturity, derivative value equals unwind value (no continuation)
    value_grid[n] = unwind_values
    
    # Boundary tracking: for each time step, store the spot level that separates exercise region
    boundary = np.full(n + 1, np.inf)
    # exercise flag per node (for output)
    exercise_flag = [None] * (n + 1)
    exercise_flag[n] = np.ones_like(spots_n, dtype=bool)  # at maturity always unwind
    
    # Variables to store exercise and continuation values at time 0
    exercise_value = None
    continuation_value = None
    
    # Backward induction from step n-1 down to 0
    for i in range(n - 1, -1, -1):
        spots = spot_grid[i]
        m = len(spots)
        continuation_values = np.zeros(m)
        # compute continuation value as risk-neutral expectation of next step values
        for j in range(m):
            up_val = value_grid[i + 1][j]
            down_val = value_grid[i + 1][j + 1]
            continuation_values[j] = np.exp(-r * dt) * (q * up_val + (1 - q) * down_val)
        
        # compute unwind values at this time step
        unwind_vals = np.zeros(m)
        for idx, spot in enumerate(spots):
            time_to_expiry = T - i * dt
            vol_low = sigma_fair_func(spot)
            vol_high = vol_low + sigma_offset
            price_low = price_func(spot, K, time_to_expiry, r, vol_low)
            price_high = price_func(spot, K, time_to_expiry, r, vol_high)
            unwind_vals[idx] = price_high - price_low
        
        # Capture exercise and continuation values at time 0 (i = 0)
        if i == 0:
            continuation_value = continuation_values[0]
            exercise_value = unwind_vals[0]
        
        # choose max between continuation and unwind
        values = np.maximum(unwind_vals, continuation_values)
        value_grid[i] = values
        
        # Determine exercise decision: unwind if unwind >= continuation
        exercise = unwind_vals >= continuation_values
        exercise_flag[i] = exercise
        
        # If any exercise at this time step, record the boundary spot
        if np.any(exercise):
            if option_type == 'call':
                # For call spreads, exercise region is above boundary → boundary is lowest spot where exercise True
                boundary[i] = np.min(spots[exercise])
            else:
                # For put spreads, exercise region is below boundary → boundary is highest spot where exercise True
                boundary[i] = np.max(spots[exercise])
    
    # Return initial value (at time 0, state 0)
    initial_value = value_grid[0][0]
    return initial_value, exercise_value, continuation_value


def test_binomial_tree():
    """Simple test case."""
    # Example parameters
    n = 100
    S0 = 100.0
    K = 100.0
    T = 1.0
    r = 0.05
    sigma_spot = 0.2
    # simple sigma_fair function: constant 0.2
    sigma_fair_func = lambda s: 0.2
    sigma_offset = 0.1  # high vol option has vol 0.3
    
    val, exercise_value, continuation_value = binomial_tree_value(
        n, S0, K, T, r, sigma_spot, sigma_fair_func, sigma_offset
    )
    print(f"Initial value: {val}")
    print(f"Exercise value: {exercise_value}")
    print(f"Continuation value: {continuation_value}")
    print(f"Exercise premium (exercise - continuation): {exercise_value - continuation_value}")
    return val


if __name__ == "__main__":
    test_binomial_tree()