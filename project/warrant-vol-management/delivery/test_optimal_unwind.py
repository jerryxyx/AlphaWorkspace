import numpy as np
import matplotlib.pyplot as plt

# Import your original script (make sure it's named cash_margin_algo.py)
import cash_margin_algo as cma
# Import the new PDE solver
import optimal_unwind_pde_solver as pde_solver

def run_tests():
    # Parameters for testing
    S0 = 100.0
    K = 100.0
    T = 1.0
    vol_high = 0.25
    vol_base = 0.20
    sigma_spot = 0.20
    option_type = 'call'

    print("=========================================================")
    print(" SCENARIO 1: STATIC PNL CALCULATIONS (Hold to Maturity)  ")
    print("=========================================================")
    print("Description: Compares the theoretical drift of the spread")
    print("against a Monte Carlo simulation if held to maturity T=1.")
    
    theo_pnl = cma.theoretical_expected_pnl(K, vol_high, vol_base, sigma_spot, option_type, S0, T)
    mc_pnl = cma.monte_carlo_expected_pnl(K, vol_high, vol_base, sigma_spot, option_type, n_samples=50000, S0=S0, T=T)
    
    print(f"\nTarget Strike : {K}")
    print(f"Theo E[PnL]   : {theo_pnl:.4f}")
    print(f"MC E[PnL]     : {mc_pnl:.4f}")
    print("Conclusion: The high-vol leg bleeds edge over time. Holding to maturity yields negative or near-zero PnL depending on K.")

    print("\n=========================================================")
    print(" SCENARIO 2: OPTIMAL UNWIND (LSM vs PDE)                 ")
    print("=========================================================")
    print("Description: Calculates the maximum expected PnL by finding")
    print("the optimal early-exercise stopping time.")
    
    # Run LSM
    print("\nRunning LSM (Stochastic Regression)...")
    lsm_pnl, lsm_S, lsm_ttm, _ = cma.lsm_optimal_pnl(K, vol_high, vol_base, sigma_spot, option_type, n_paths=5000, n_steps=50, S0=S0, T=T)
    
    # Run PDE
    print("Running PDE (HJB Finite Difference LCP)...")
    pde_pnl, pde_spread, pde_S_min, pde_S_max, pde_ttm = pde_solver.pde_optimal_unwind(K, vol_high, vol_base, sigma_spot, option_type, T=T, S0=S0)
    
    print(f"\nResults for Strike {K}:")
    print(f"LSM Optimal E[PnL] : {lsm_pnl:.4f}")
    print(f"PDE Optimal E[PnL] : {pde_pnl:.4f}")
    print("Conclusion: The PDE avoids the variance of Monte Carlo regression, usually finding a slightly tighter and more accurate optimal value.")

    # Graphing the Boundaries
    plt.figure(figsize=(12, 6))
    
    # Plot PDE Boundaries
    plt.plot(pde_ttm, pde_S_min, 'b-', linewidth=2, label='PDE Exercise Boundary (Lower S*)')
    plt.plot(pde_ttm, pde_S_max, 'b--', linewidth=2, label='PDE Exercise Boundary (Upper S*)')
    
    # Plot LSM Boundaries (Mean S*)
    # Note: LSM usually extracts a mean exercise point per time step, not strict upper/lower bounds.
    plt.scatter(lsm_ttm, lsm_S, color='red', marker='x', alpha=0.6, label='LSM Mean Exercise State')
    
    plt.axhline(K, color='green', linestyle=':', label=f'Strike K={K}')
    plt.axhline(S0, color='black', linestyle='-.', alpha=0.5, label='Initial Spot S0')
    
    plt.title(f'Optimal Unwind Boundary: PDE vs LSM (Strike={K})')
    plt.xlabel('Time to Maturity (Years)')
    plt.ylabel('Spot Price (S)')
    plt.xlim(1.0, 0.0) # Standard to show TTM decreasing from left to right
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('pde_vs_lsm_boundary.png', dpi=300)
    print("\n=> Graph saved as 'pde_vs_lsm_boundary.png'")
    plt.show()

if __name__ == "__main__":
    run_tests()