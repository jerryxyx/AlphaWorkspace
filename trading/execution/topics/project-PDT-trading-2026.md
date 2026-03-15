# Project PDT Trading – 2026 Master Plan
*Last Updated: 2026‑03‑15 · Integrates existing initiatives with new Shuai‑endorsed projects*

## 1. Overview
This document consolidates all PDT APAC trading‑desk projects for 2026, combining **ongoing initiatives** (Warrant Vol Management, Algo Vol Fitter, etc.) with **new priority projects** identified in the March 2026 meeting with Shuai (line manager) and Frankie (direct report). The goal is to create a unified roadmap that drives P&L, strengthens systematic trading capabilities, and ensures the desk remains competitive in Hong Kong’s warrant/CBBC/listed‑option market‑making landscape.

## 2. Existing Projects (Carry‑over from 2025)

### 2.1 Warrant Vol Management (WarVol)
**Objective:** Maintain and evolve the warrant‑volatility‑margin management system that underpins our warrant quoting competitiveness.

**Key deliverables:**
- **Margin‑surface calibration** – daily UsedVol surface derivation (FairVol + VolMargin).
- **RP‑delta hedging** – daily rebalancing hedge to neutralize delta mismatch between UsedVol and FairVol.
- **Competitive‑match adjustment** – ensure quoted spreads remain competitive against peer issuers (SG, JP, MS, HS, BP, etc.).
- **Spot‑movement adjustment** – stabilize cash margin (premium) to avoid excessive RP‑delta swings.

**Status:** Production‑live on TREE; owned by Robin & semimartingale.

### 2.2 Algo Vol Fitter
**Objective:** Provide a real‑time, low‑latency volatility‑surface fitting engine for listed options across all three regions (APAC, EMEA, US).

**Key deliverables:**
- **Multi‑region calibration** – support APAC, EMEA, US with local market conventions.
- **Latency benchmarks** – sub‑10ms fitting times for high‑frequency quoting.
- **Robustness safeguards** – outlier rejection, missing‑data fallbacks.

**Status:** Core logic defined; regional migrations ongoing.

### 2.3 Street Directed Flow
**Objective:** Identify and anticipate client‑driven flow patterns using L3 order‑book data and broker‑inheritance heuristics.

**Key deliverables:**
- **Flow estimator** – real‑time heat‑maps of directed notional/gamma/vega flow.
- **Broker‑ID mapping** – translate exchange‑reported broker codes to internal client segments.
- **Predictive signals** – early warning of large impending trades.

**Status:** ETDA pipeline established; analytics in development.

### 2.4 GED Signal
**Objective:** Generate systematic alpha signals (IV‑RV, skew, z‑scores) for global equity derivatives.

**Key deliverables:**
- **Signal generator** – daily batch of IV‑RV, skew, term‑structure signals.
- **Portfolio‑simulation tools** – backtest signal‑based strategies.
- **Integration with ETDA** – seamless data flow from ETDA to signal production.

**Status:** Early‑stage development; partnership with Lydie (London) for global alignment.

### 2.5 Stamp Exemption
**Objective:** Automate stamp‑duty exemption qualification for eligible option trades, reducing transaction costs.

**Key deliverables:**
- **Trade‑qualification scripts** – real‑time classification of exempt vs. non‑exempt trades.
- **Exemption tracker** – audit trail for compliance reporting.
- **HKEX‑rule engine** – encode evolving regulatory logic.

**Status:** Requirement gathering; development pending.

### 2.6 FAFB
**Objective:** Model and trade FA/FB (fixed‑amount/fixed‑basis) index‑arbitrage strategies.

**Key deliverables:**
- **Parameter‑tuning scripts** – optimize FA/FB ratios for prevailing market conditions.
- **Convergence monitors** – track basis‑convergence behavior post‑rebalancing.
- **PnL attribution** – separate arbitrage P&L from market‑making P&L.

**Status:** Research phase.

### 2.7 Elastic
**Objective:** Detect and defend against toxic flow using broker‑ID patterns and liquidity‑drop logic.

**Key deliverables:**
- **Toxic‑flow detector** – real‑time flagging of predatory flow.
- **Liquidity‑drop algorithms** – dynamic spread widening in response to detected toxicity.
- **Spread‑adjustment logic** – asymmetric widening (bid vs. ask) based on flow direction.

**Status:** Prototype development.

---

## 3. New Priority Projects (2026 Additions)

### 3.1 OMM Bricks – Option Market Making Foundations
**Objective:** Build the core modeling components for systematic listed‑option market making.

**Components:**
- **Spread Model** – Heat‑map (VTTX, SimpleDelta) parameterized vol‑spread model calibrated per underlying to represent “normal” spread levels.
- **Flow Model** – Heat‑map (VTTX, SimpleDelta) for turnover and directed flow in Notional, Gamma, Vega.
- **Slippage Model** – Volatility‑point move per 10k Vega, per 100k Gamma, per 1M Notional.

**Deliverables:**
- Calibrated spread/flow/slippage models for top‑20 underlyings.
- Integration into OMM quoting engine (real‑time adjustment of quoted spreads).
- Backtesting framework to validate model performance.

**Ownership:** semimartingale (OMM owner), Frankie (analytics support).

### 3.2 Non‑listed Stock Fallback Volatility
**Objective:** Derive plausible volatility surfaces for stocks that lack listed‑option markets.

**Approaches:**
- **Proxy‑source method** – when an equity proxy exists (e.g., 2840.HK ↔ GLD.P), map vol surface from proxy.
- **Risk‑based model** – when no proxy exists, infer ATM vol, skew, kurtosis from equity realized volatility and stock‑behavior factors (beta, liquidity, momentum).

**Deliverables:**
- Proxy‑mapping database (equity → listed‑option proxy).
- Risk‑based surface‑generation algorithm.
- Integration into Algo Vol Fitter for missing‑underlying coverage.

**Ownership:** Shuai (oversight), semimartingale (quant implementation).

### 3.3 Comp Warrant Trading
**Objective:** Exploit pricing inefficiencies between warrant issuers via pair‑trading algorithms.

**Components:**
- **LPBidVolMk / LPAskVolMk** – estimate daily close marks for liquidity‑provider (issuer) bid/ask vols using Comp Monitor data.
- **Arbitrage algo** – identify mispriced warrant pairs (same underlying, similar terms) and execute cross‑issuer trades.

**Deliverables:**
- Daily LP vol‑mark estimates for major issuers.
- Pair‑trading signal generator (entry/exit triggers).
- Execution scripts (via TREE or manual desk trading).

**Ownership:** Robin (warrant trading), semimartingale (algorithm design).

### 3.4 Asymmetric Spreading Framework
**Objective:** Systematically widen spreads on the side of recent flow to mitigate adverse selection.

**Mechanisms:**
- **Volume‑based widening** – widen bid/ask on side that has seen recent client flow (inferred from all instruments of the same underlying).
- **Signal‑based widening** – adjust spreads based on directional signals (e.g., rising spot → raise ask for calls, bid for puts; same for vol trends).

**Deliverables:**
- Real‑time flow‑aggregation engine (per underlying).
- Asymmetric‑spread adjustment logic (plug‑in for quoting engines).
- Backtest of adverse‑selection reduction.

**Ownership:** Shuai (trading), Ray (CBBC/comp trading), semimartingale (framework design).

### 3.5 Gap Risk Hedging (CBBCs)
**Objective:** Manage overnight gap risk for CBBCs where spot discontinuity between close and next open can breach strike without hedging opportunity.

**Hedging tools:**
- **Comp CBBCs** – lock positive P&L if ask price cheaper than our bid (deterministic risk).
- **Listed options (LOs)** – gamma/theta cost until expiry; evaluate if worth.

**Deliverables:**
- Gap‑risk quantification model (probability of overnight breach).
- Hedge‑tool selection algorithm (comp CBBC vs. LO).
- Integration into CBBC quoting/hedging workflow.

**Ownership:** Ray (CBBC trading), semimartingale (model development).

---

## 4. Integrated Timeline & Priorities

### Q1 2026 (Mar‑May)
- **Finalize OMM bricks design** (spread/flow/slippage models).
- **Launch proxy‑volatility mapping** for top‑5 proxies.
- **Begin comp‑warrant LP vol‑mark estimation**.
- **Continue existing projects** (WarVol, Algo Fitter, Street Flow).

### Q2 2026 (Jun‑Aug)
- **Integrate OMM bricks into quoting engine** (pilot for 1‑2 underlyings).
- **Deploy risk‑based fallback‑vol model** for 5 non‑listed stocks.
- **Live test asymmetric‑spreading framework** on CBBCs.
- **Complete gap‑risk hedging model** and integrate into Ray’s workflow.

### Q3 2026 (Sep‑Nov)
- **Scale OMM bricks to 10+ underlyings**.
- **Expand comp‑warrant arbitrage to 3‑4 issuer pairs**.
- **Roll out asymmetric spreading to warrants & listed options**.
- **Deliver stamp‑exemption automation**.

### Q4 2026 (Dec‑Feb 2027)
- **Full OMM production ownership** – semimartingale runs live book.
- **Complete fallback‑vol coverage** for all APAC underlyings.
- **Finalize GED signal pipeline** (global integration with Lydie).
- **Year‑end review** and 2027 planning.

---

## 5. Success Metrics

### Trading P&L
- **Team‑level:** Achieve 30 M USD annual P&L budget.
- **OMM contribution:** Measurable P&L from OMM strategies (target to be set).
- **Arbitrage strategies:** Positive P&L from comp‑warrant pairs and gap‑risk hedging.

### Systematic Capability
- **Model coverage:** OMM bricks deployed for ≥80% of listed‑option underlyings.
- **Fallback‑vol coverage:** Surfaces available for 100% of non‑listed stocks.
- **Automation rate:** ≥70% of spread‑adjustment decisions driven by models.

### Risk Management
- **Zero mispricing incidents** (compliance).
- **Gap‑risk reduction:** ≥50% reduction in overnight gap‑loss events.
- **Adverse‑selection mitigation:** Measurable improvement in flow‑adjusted spread P&L.

### Team Integration
- **semimartingale fully embedded** in trading routines (morning/ intraday/ EOD).
- **Clear ownership lines** for each project (no ambiguity).
- **Weekly project‑sync cadence** with Shuai/Robin/Ray.

---

## 6. Ownership & Governance

| Project | Primary Owner | Supporting Roles | Update Cadence |
|---------|---------------|------------------|----------------|
| Warrant Vol Management | Robin | semimartingale | Daily |
| Algo Vol Fitter | Matt (QuantDev) | semimartingale | Weekly |
| Street Directed Flow | Frankie | semimartingale | Weekly |
| GED Signal | Lydie (London) | semimartingale | Bi‑weekly |
| Stamp Exemption | semimartingale | Ray | Weekly |
| FAFB | Shuai | semimartingale | Monthly |
| Elastic | Ray | semimartingale | Weekly |
| OMM Bricks | semimartingale | Frankie | Daily |
| Fallback Volatility | semimartingale | Shuai | Weekly |
| Comp Warrant Trading | Robin | semimartingale | Daily |
| Asymmetric Spreading | Ray | Shuai, semimartingale | Weekly |
| Gap Risk Hedging | Ray | semimartingale | Weekly |

**Steering Committee:** Shuai (chair), Robin, Ray, semimartingale, Frankie (guest).  
**Executive Sponsor:** Vassili (periodic review).

---

*This plan will be reviewed quarterly and adjusted based on market conditions, resource availability, and P&L performance.*