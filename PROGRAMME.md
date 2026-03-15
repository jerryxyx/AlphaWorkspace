# Agent Programme (Proposed Digest)
*Version: Draft 1.0 · Last Updated: 2026‑03‑09 · Author: OpenClaw Agent*  
**Status:** Proposed restructure for review – not final.  

---

## Table of Contents
- [Introduction](#introduction)
- [Self‑Improving](#selfimproving)
  - [Skills Upgrade](#skills-upgrade)
  - [Model Optimization](#model-optimization)
  - [Structured Memory & Analysis](#structured-memory--analysis)
  - [Routine](#routine)
- [Roles](#roles)
- [Trading](#trading)
  - [Structure](#structure)
  - [Execution](#execution)
  - [Product‑Specific Knowledge](#product-specific-knowledge)
    - [DLC](#dlc)
    - [Warrant](#warrant)
    - [CBBC](#cbbc)
    - [Listed Option](#listed-option)
- [Project](#project)
  - [FAFB](#fafb)
  - [Elastic](#elastic)
  - [Stamp Exemption](#stamp-exemption)
  - [Warrant Vol Management](#warrant-vol-management)
  - [Algo Vol Fitter](#algo-vol-fitter)
  - [Street Directed Flow](#street-directed-flow)
  - [GED Signal](#ged-signal)
  - [Alpha](#alpha)
- [Appendix: Implementation Notes](#appendix-implementation-notes)
- [Glossary](#glossary)

---

## Introduction
This Programme defines the performance expectations and development roadmap for the OpenClaw agent (hereafter “the Agent”). It serves as a living document that will evolve through collaborative review between the human operator (“Operator”) and the Agent.  

**Key principles:**
- **Two‑version system:** Maintain both a raw (Operator‑authored) draft and a digested (Agent‑refined) version.
- **Iterative refinement:** The Agent may challenge, optimise, and propose updates to the Programme, subject to Operator sign‑off.
- **Version control:** All critical documents are tracked via Git and synced to a remote repository.
- **Wisdom as hyper‑parameters:** The high‑level knowledge captured here acts as foundational “wisdom” that guides the Agent’s reasoning and tooling choices.

---

## Self‑Improving
### Skills Upgrade
Grant the Agent access to powerful, high‑quality toolkits (OpenClaw skills) that extend its operational capabilities. Skills are installed, configured, and documented in the workspace.

### Model Optimization
**Goal:** Dynamically select the most appropriate AI model (intelligence) for each task, balancing cost, latency, and reasoning quality.  
**Long‑term vision:** A core “brain” that orchestrates multi‑model calls within a single reasoning session, using a structured local memory to retain context across switches.  

**Current state:** DeepSeek is already configured as a provider; hybrid calling (e.g., blending DeepSeek for financial reasoning with xAI/Grok for general tasks) remains a future capability to explore.

### Structured Memory & Analysis
**Concept:** A knowledge system that organises the Agent’s domain understanding into a navigable directory and file structure under the OpenClaw workspace.  
**Implementation:**
- A root‑level file maps the knowledge tree and provides summary references.
- Weekly reviews to audit additions/removals, ensuring the knowledge base stays relevant and accurate.
- Daily Git commits to preserve version history.

**Purposes:**
1. **Structured reasoning:** Decisions become traceable and objective; the Operator can quickly inspect the Agent’s “mind”.
2. **Iterative learning:** The Agent learns from past failures and refines its knowledge‑filtering heuristics.
3. **Portability:** Knowledge is decoupled from the underlying LLM; the reference tree can be cloned to new machines, providing a baseline “brain” that accelerates re‑learning (analogous to a trader’s notes after a multi‑year gap).

### Routine
**Weekly review (triggerable ad‑hoc):**
- Programme document
- Roles report
- Knowledge report

---

## Roles
Roles are capability profiles that build upon basic skills. A single Agent can hold multiple roles, analogous to a trader who also manages projects and drives innovation.  

**Initial roles:**
1. **Trading Execution** – day‑to‑day market‑making, flow management, risk monitoring.
2. **Trading Project** – systematic/algo development, quantitative research.

**Folder structure per role:**  
*Note: The `roles/` folder has been merged into `trading/` and `project/` domains. Execution content lives under `trading/execution/`; project content lives under `project/*/` (each project has its own `topics/` and `delivery/` subfolders). The original per‑role folder pattern is still conceptually valid but physically integrated into the domain‑based structure.*

```
Role/
├── topics/      # knowledge, research, notes
└── delivery/    # scripts, dashboards, outputs
```

Even execution‑role scripts should include pre‑market, intraday, and post‑market summaries to optimise Operator attention.

---

## Trading
### Structure
Maintain a professional framework per product type. HK public‑distribution desk covers:
1. Derivative Warrants
2. CBBCs (Callable Bull/Bear Contracts)
3. Listed Options
4. DLC (Derivative Linked Certificates)

Each product has its own folder for knowledge and delivery.

### Execution
An overarching folder that integrates all products, logging trading attention from morning to evening, weekdays to weekends.  

**Pre‑market focus:**
- Ex‑dividend dates
- Spot moves
- News with potential major spot impact
- Vol‑surface conduction (HSI stock‑vol opens at 9:15; spot market at 9:15/9:20)

**Pricing‑engine parameters:**
```
UsedVol   = ManVol(editable) + ManVolTraderOffset(editable) + ManVolOffset(algo) + AdjVol(algo)
DeltaSpreadBid/Ask (editable)
Tick/Cash spread (trader‑tweakable)
```

**Decision tree needed** for symmetric (margin) vs. asymmetric (spreading) price adjustments.

**KO (knock‑out) event management (CBBCs):**
- Intraday KO → adjust Delta (remove expired instrument’s delta).
- Overnight gap risk → hedge by buying competitor products (e.g., BNP) if cheap; otherwise raise DeltaMargin to buy back client positions.
- **TV profile:** Keep the risk (stress) profile within TV‑20% to TV+20% (i.e., theoretical‑value changes under spot shocks should stay within ±20% of current book value).

**Dashboard metrics:**
- P&L
- Delta/Vega/Gamma per underlying & product type
- SlippageProduct (trade vs. engine mid)
- SlippageHedge (hedge execution)
- Recent spot moves, positions

**Evening tasks:**
- Update market parameters for next day’s pricing grids.
- Assess margin/spread for new listings and existing products:
  - Compare cheapness vs. competitors.
  - Review 5‑day historical path (if OI > 0); otherwise adjust arbitrarily.
  - Raise margins (beneficial to bought clients) easier than dropping.
- Adjust HF/VA penalty algos (drop price for intraday positive position; recover margin when they sell back).

### Product‑Specific Knowledge
#### DLC
Path‑dependent instrument with formula driven by past/future market data (spot, strike, div, rates).  
**Daily support:** Replicate intrinsic value and verify against termsheet.  
**Variants:** {HK/SG/US} × {Index/Stock} × {Call/Put}. Need leading formulas and differences.

#### Warrant
Asian option (single‑stock, last‑5‑day averaging) or European option (indices). Issued by banks (UBS, JP, BNP, SocGen, MS, etc.).

#### CBBC
Barrier option with knock‑out before underlying touches strike. Residual value after KO depends on minimum (Bulls/Calls) or maximum (Bears/Puts) spot during remaining sessions.

#### Listed Option
Decentralised; participants can net short positions. American (single‑stock) or European (indices).  
**OMM obligations:** >70% continuous quoting monthly.  
**Current projects:**
- Speed‑up order routing to counter spot‑driven toxic flow.
- Stamp‑duty exemption via OMM role (see Project section).

---

## Project
### FAFB
FA/FB parameters widen quoting spreads during known events (market open, macro releases) and converge gradually, pausing if hit/lift occurs.

### Elastic
Transaction algo that reacts to toxic flow (identified by client broker‑ID) by dropping liquidity (decline bid, widen spread).

### Stamp Exemption
**Goal:** Use OMM‑account stock trades (for option hedging) to fill stamp‑duty‑exempt quotas, saving duty on other desk flows.  
**Mechanics:** Legitimate hedging trades are exempt; simulate option flows to identify qualifying stock trades.

### Warrant Vol Management
Two sub‑topics:

**1. Cash margin** – mathematical derivation & practical validation.  
**2. Vol following** – direct, using vol‑fitter infrastructure.

**Pricing model:**  
`UsedVol = FitVol + VolMg`  
Profitability comes from FitVol accuracy and margin management.

**Pair‑trading perspective:**  
Cash margin ≈ (UsedVol – FitVol) × Vega.  
To keep cash margin flat over time:  
`UsedVol(t₁) = UsedVol(t₀) + FitVolMv(t₁) + (VegaRatio(t₁) – 1) × VolMg(t₀)`  

- **FitVolMv:** Real‑time fair‑vol movement (provided by Algo Vol Fitter).  
- **VolMg:** Must be shaped as a surface (high OTM/ITM, low ATM) to avoid statistical arbitrage. Derive theoretical breakeven surface via Black‑Scholes + Monte Carlo validation.

### Algo Vol Fitter
Real‑time (<1 s) low‑latency fitter reflecting listed‑option market.

### Street Directed Flow
Predict flow against market makers using:
- L3 order data + broker‑queue integration.
- Pattern detection & broker‑inheritance logic.
- Daily issuer‑reported volume/net‑positions for cross‑validation.

**Alpha signal:** Thresholded flow estimator that reveals risk‑preference propagation from warrant to listed‑option market.  
**Delivery:** Live dashboard with three heatmaps (warrants, listed options, conduction comparison) per underlying.

### GED Signal
Classic option‑metrics calculation:
- Implied vs. realised vol (IV‑RV)
- Call/put skew
- Historical z‑scores

**Backtesting portfolio:**  
Example strategy: if IV‑RV z‑score > +3, sell gamma (1M liquid options + delta hedge); if < –3, buy gamma. Hold to expiry.

**Learning materials:** The Agent should compile thorough educational resources on these metrics to accelerate Operator knowledge acquisition.

### Alpha
**UsedULP = ULP(Bid,Ask,Sizes) + alpha**  
Sub‑projects:
- Lead‑lag analysis (PCA on index/components).
- Order‑flow‑driven ULP‑spread widening.
- Multi‑level hit/lift detection → adjust pricing side (InstrumentBid/Ask = f(ULPAsk/ULPBid, VolBid/VolAsk, …)).

**Status:** Details pending future Operator input (as per original draft).

---

## Appendix: Implementation Notes
- All proposed folder structures will be created under `/Users/xyx/.openclaw/workspace/`.
- Weekly review scheduled via OpenClaw cron.
- Model performance (DeepSeek, xAI/Grok) can be tracked in `business‑documents/` if hybrid calling is explored.
- Knowledge‑tree root file: `workspace/knowledge/INDEX.md`.

---

## Glossary
| Term | Meaning |
|------|---------|
| OI | Open Interest |
| TV | Theoretical Value (mid‑price before tick rounding); also refers to risk/stress profile (TV±20% bounds) |
| ULP | Underlying Price |
| VolMg | Volatility Margin |
| FitVol | Fitted (fair) volatility |
| KO | Knock‑Out (CBBC barrier breach) |
| OMM | Option Market Maker |
| HF | Hedge Fund |
| VA | Volatility Arbitrageur |
| DLC | Derivative Linked Certificate |
| CBBC | Callable Bull/Bear Contract |

---

*Proposed by OpenClaw Agent on 2026‑03‑09. Pending Operator review and sign‑off.*