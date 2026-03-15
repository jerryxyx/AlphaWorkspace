# Knowledge Index
*Root map of the OpenClaw workspace · Last Updated: 2026‑03‑12*

This file is the central index of the Agent’s structured knowledge system. It provides a hierarchical outline of all domains (roles, trading, projects, memory, etc.) with cross‑references to key files.

**How to use:**
- Navigate the workspace by following the links below.
- During weekly reviews, update this index to reflect additions, removals, or reorganizations.
- The index is independent of the underlying LLM; cloning this tree to a new machine restores the “brain”.

---



## 1. Knowledge Domains
Deep, domain‑specific notes referenced by the index.

### 1.1 Trading Knowledge
- Product specifications, market mechanics, risk concepts
- *Files*: [warrant basics](knowledge/trading/warrant‑basics.md), [CBBC mechanics](knowledge/trading/cbbc‑mechanics.md), [listed‑option obligations](knowledge/trading/listed‑option‑obligations.md), [index basis arbitrage](knowledge/trading/index-basis-arbitrage.md), [warrant vol margin management](knowledge/trading/warrant-vol-margin-management.md), [cash‑margin arbitrage](knowledge/trading/cash‑margin‑arbitrage.md), [warrant papers grouped summary](../../business-documents/warrant-papers-grouped-summary.md)

### 1.2 Quantitative Knowledge
- Models, formulas, derivations, numerical methods
- *Files*: [Black‑Scholes extensions](knowledge/quantitative/black‑scholes‑extensions.md), [vol‑surface math](knowledge/quantitative/vol‑surface‑math.md)

### 1.3 Operational Knowledge
- Tools, processes, Git workflows, OpenClaw skill usage
- *Files*: [daily Git routine](knowledge/operational/daily‑git‑routine.md), [weekly review checklist](knowledge/operational/weekly‑review‑checklist.md)

---

## 2. Trading
Desk‑level organization mirroring the HK public‑distribution desk.

### 2.1 Products
#### 2.1.1 Warrants
- **Topics**: [Asian/European specs](trading/products/warrants/topics/specs.md), issuer details, pricing conventions
- **Delivery**: [pricing script](trading/products/warrants/delivery/pricing.py), margin calculators

#### 2.1.2 CBBCs
- **Topics**: barrier‑option mechanics, KO/residual‑value formulas, TV‑profile bounds
- **Delivery**: KO‑hedge scripts, TV‑profile monitors

#### 2.1.3 Listed Options
- **Topics**: OMM obligations, American/European differences, speed‑optimization needs
- **Delivery**: order‑routing scripts, stamp‑exemption tools

#### 2.1.4 DLC
- **Topics**: path‑dependent formulas, term‑sheet variants, daily verification steps
- **Delivery**: intrinsic‑value replicators, daily‑check scripts

### 2.2 Execution
Cross‑product trading‑execution support.
- **Topics**: [pre‑market checklist](trading/execution/topics/pre‑market‑checklist.md), intraday alerts, KO handling, [PDT 2026 objectives](trading/execution/topics/PDT‑2026‑objectives.md), [Vassili catch‑up talking points](trading/execution/topics/Vassili‑catchup‑2026‑03‑16.md)
- **Delivery**: [dashboard](trading/execution/delivery/dashboard.py), morning reports, P&L/risk monitors, slippage trackers

---

## 3. Projects
Ongoing initiatives with clear separation of knowledge (`topics/`) from deliverables (`delivery/`).

### 3.1 Warrant Vol Management
- **Topics**: cash‑margin math, vol‑surface research, margin‑surface derivation
- **Delivery**: Monte‑Carlo simulations, margin‑surface generator

### 3.2 Algo Vol Fitter
- **Topics**: real‑time vol‑fitting algorithms, data pipelines, latency requirements
- **Delivery**: fitter implementation, latency benchmarks

### 3.3 Street Directed Flow
- **Topics**: L3 order data, broker inheritance, flow‑prediction models
- **Delivery**: flow estimator, heat‑map dashboards

### 3.4 GED Signal
- **Topics**: IV‑RV, skew, z‑score calculations, backtesting frameworks
- **Delivery**: signal generator, portfolio‑simulation tools

### 3.5 Stamp Exemption
- **Topics**: HKEX rules, option‑flow simulation, stamp‑duty logic
- **Delivery**: trade‑qualification scripts, exemption tracker

### 3.6 FAFB
- **Topics**: FA/FB parameters, event‑driven spread widening, convergence behavior
- **Delivery**: parameter‑tuning scripts, convergence monitors

### 3.7 Elastic
- **Topics**: toxic‑flow detection, broker‑ID patterns, liquidity‑drop logic
- **Delivery**: liquidity‑drop algorithms, spread‑adjustment logic

### 3.8 Alpha
- **Topics**: lead‑lag PCA, order‑flow spread models *(placeholder)*
- **Delivery**: *(placeholder for future deliverables)*

---

## 4. Infrastructure
General‑purpose tooling for network access, system configuration, and real‑world survival.

### 4.1 VPN / Proxy Management
- **Topics**: [Clash Verge operations](infrastructure/vpn/topics/clash‑verge‑ops.md)
- **Delivery**: [fastest‑non‑HK selector](infrastructure/vpn/delivery/clash_fastest_non_hk.py), [group latency tester](infrastructure/vpn/delivery/clash_speed_test.py)

### 4.2 Browser Automation
- **Best practices**: [Browser automation guide](infrastructure/browser‑best‑practices.md) (context control, compact snapshots, stable refs)

---

## 5. Memory
Temporal logs for raw events, weekly summaries, and curated long‑term insights.

### 5.1 Daily Logs
- [2026‑03‑10](memory/daily/2026‑03‑10.md) *(today)*
- *Older logs*: `memory/daily/YYYY‑MM‑DD.md`

### 5.2 Weekly Summaries
- [2026‑03‑15 summary](memory/weekly/2026‑03‑15‑summary.md), older summaries: `memory/weekly/`

### 5.3 Long‑Term Memory
- Curated insights distilled from daily logs *(eventually merged into `MEMORY.md` for main‑session use)*

---

## 6. Programme
The foundational Agent Programme and its evolution.

- **Raw original**: [AgentProgramme.txt](programme/raw/AgentProgramme.txt)
- **Digested version**: [PROGRAMME.md](../PROGRAMME.md)
- **Architecture proposal**: [architecture‑proposal.md](programme/architecture‑proposal.md)
- **Review notes**: `programme/reviews/`

---

## 7. External References
- **Business documents**: `business‑documents/` (papers, reports, competitor analysis)
- **OpenClaw skills**: `skills/` (installed toolkits)

---

## Update Log
| Date | Change | Updated by |
|------|--------|------------|
| 2026‑03‑10 | Initial skeleton created | OpenClaw Agent |
| 2026‑03‑11 | Added morning reports to Execution delivery | OpenClaw Agent |
| 2026‑03‑15 | Weekly review completed; updated cash‑margin‑arbitrage.md, warrant‑vol‑margin‑management.md, cash‑margin‑arbitrage‑papers.md with new academic findings | OpenClaw Agent |
| 2026‑03‑15 | Added browser automation best practices guide (infrastructure/browser‑best‑practices.md) | OpenClaw Agent |
| 2026‑03‑15 | Added PDT 2026 objectives and Vassili catch‑up talking points to Execution topics | OpenClaw Agent |

---

*This index is maintained as part of the Agent Programme’s structured‑memory system. Refer to [PROGRAMME.md](../PROGRAMME.md) for the full context.*