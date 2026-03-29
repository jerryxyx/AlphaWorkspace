# Warrant Volatility Management
*Project Note · Last Updated: 2026‑03‑29 · Status: Active*

---

## Objective
Implement numerical methods and analytical frameworks to support **warrant volatility‑margin management**—specifically, to:
1. Model the **cash‑margin arbitrage** between warrants and listed options.
2. Derive the **vol‑margin surface** that avoids statistical arbitrage.
3. Provide validated numerical solvers for arbitrage‑derivative valuation (call/put spreads with early‑exercise decisions).

## Knowledge Foundation
This project builds on the analysis captured in:
- [[knowledge/trading/warrant‑vol‑margin‑management]] – cash‑margin phenomenon, toxic‑flow behavior, vol‑margin surface bootstrapping, and academic calibration methods.

The theoretical framework is defined in the Agent Programme:
- [[PROGRAMME.md#warrant‑vol‑management]] – pricing model (`UsedVol = FitVol + VolMg`), pair‑trading perspective, and surface‑shaping requirements.

## Deliverables
### Code Suite (`delivery/`)
A Python‑based numerical‑methods suite for arbitrage‑derivative valuation:
- **Lattice (binomial tree)** – supports call/put spreads, early‑exercise boundary detection, boundary plots.
- **Monte Carlo LSM** – least‑squares Monte Carlo with antithetic variates.
- **PDE solver** – finite‑difference with PSOR for early‑exercise constraint (under refinement).
- **Volatility‑function library** – configurable `σ_fair(s)` shapes (constant, smile, skew).
- **Cross‑method validation** – compares values, premiums, and exercise boundaries across all three methods.
- **Jupyter notebook** – interactive visualization of binomial tree, exercise decisions, and boundary analysis.

See [[project/warrant‑vol‑management/delivery/SUMMARY.md|detailed summary]] for current status and results.

### Knowledge Outputs
- Updated [[knowledge/trading/warrant‑vol‑margin‑management]] with implementation references.
- Weekly summaries tracking progress (e.g., [[memory/weekly/2026‑03‑29‑summary.md]]).

## Current Status
**Active development.**  
- **Lattice & Monte Carlo:** production‑ready; agree within machine precision.  
- **PDE solver:** functional but requires boundary‑detection fixes.  
- **Key finding:** For tested parameters (constant/smile volatility), early‑exercise premium is **zero**—immediate unwinding is optimal.  
- **Next exploration:** Design stronger spot‑dependent volatility functions that yield positive early‑exercise premiums.

**Recent milestones:**
- 2026‑03‑24: Lattice extended to call/put spreads, boundary analysis across `σ_spot`.  
- 2026‑03‑25: Cross‑method validation completed; boundary comparison across lattice, PDE, Monte Carlo.  
- 2026‑03‑29: Programme and knowledge linkages established; weekly review conducted.

## Connections
### Related Projects
- **Algo Vol Fitter** (`project/algo‑vol‑fitter/`) – provides real‑time `FitVol` inputs.  
- **Street Directed Flow** (`project/street‑directed‑flow/`) – toxic‑flow detection complements margin‑arbitrage analysis.

### External References
- **SIMM (Standard Initial Margin Model)** – vega‑based margin aggregation.  
- **Vega‑weighted calibration** (Huang et al. 2020) – objective function for surface fitting.  
- **Minimum‑Variance Delta calibration** (Zhou 2025) – constrained optimization for stable vol‑surface calibration.

### Programme Integration
This project directly implements the **Warrant Vol Management** section of the Agent Programme. Results feed back into the knowledge base, supporting iterative refinement of the Programme’s strategic guidance.

---

## Update Log
| Date | Change |
|------|--------|
| 2026‑03‑29 | Project note created with full wikilink mesh. |

---
*This file is part of the OpenClaw workspace’s structured‑documentation system. Refer to [[knowledge/INDEX.md]] for the full domain map.*