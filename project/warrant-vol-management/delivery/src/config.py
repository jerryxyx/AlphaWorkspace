"""
Configuration parameters for the arbitrage derivative valuation.
"""
import numpy as np

# Base parameters
BASE_PARAMS = {
    'S0': 200.0,
    'K': 100.0,
    'T': 1.0,               # years
    'r': 0.05,              # risk-free rate
    'sigma_spot': 0.2,      # true spot diffusion
    'sigma_offset': 0.1,    # vol margin for high-vol option
}

# Function for sigma_fair(spot). Default: constant 0.2
def sigma_fair_constant(spot: float) -> float:
    return 0.2

# Volatility smile: higher volatility when spot is far from strike
def sigma_fair_smile(spot: float, K: float = 100.0) -> float:
    """Volatility smile: baseline 20% + 10% per log-distance from strike."""
    rel = abs(np.log(spot / K))
    return 0.2 + 0.1 * rel

# Volatility skew: decreasing with spot (typical for equity options)
def sigma_fair_skew(spot: float, K: float = 100.0) -> float:
    """Volatility skew: higher volatility for lower spot."""
    return 0.3 - 0.001 * (spot - K)

# Step function: different regimes
def sigma_fair_step(spot: float) -> float:
    if spot < 80:
        return 0.25
    elif spot < 120:
        return 0.2
    else:
        return 0.15

# Lattice method parameters
LATTICE_PARAMS = {
    'n': 200,               # number of time steps
}

# Monte Carlo LSM parameters
MC_PARAMS = {
    'n_paths': 10000,
    'n_steps': 50,
    'basis_funcs': None,    # default: constant, spot, spot^2
}

# PDE finite difference parameters
PDE_PARAMS = {
    'S_min': 1.0,
    'S_max': 300.0,
    'n_S': 200,
    'n_t': 100,
    'method': 'cn',
}