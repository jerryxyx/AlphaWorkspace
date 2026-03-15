# PDT 2026 Project Landscape & Personal Objectives Mapping
*Last Updated: 2026‑03‑15 · Visualizes how personal objectives align with desk‑wide projects*

## 1. Overview: The Complete Project Landscape

| Project | Primary Owner | Key Deliverables | Status | Priority |
|---------|---------------|------------------|--------|----------|
| **Warrant Vol Management** | Robin (semimartingale support) | Margin‑surface calibration, RP‑delta hedging, competitive‑match adjustment, spot‑movement adjustment | Production‑live on TREE | High |
| **Algo Vol Fitter** | Matt (QuantDev) | Multi‑region calibration, latency benchmarks, robustness safeguards | Regional migrations ongoing | High (GED) |
| **Street Directed Flow** | Frankie (semimartingale oversight) | Flow estimator, broker‑ID mapping, predictive signals | ETDA pipeline established | Medium |
| **GED Signal** | Lydie (London) | Signal generator (IV‑RV, skew, z‑scores), portfolio‑simulation tools | Early‑stage development | Medium (GED) |
| **Stamp Exemption** | semimartingale | Trade‑qualification scripts, exemption tracker, HKEX‑rule engine | Requirement gathering | Medium |
| **FAFB** | Shuai | Parameter‑tuning scripts, convergence monitors, PnL attribution | Research phase | Low |
| **Elastic** | Ray | Toxic‑flow detector, liquidity‑drop algorithms, spread‑adjustment logic | Prototype development | Medium |
| **OMM Bricks** | semimartingale | Spread model, flow model, slippage model for listed options | Design phase | **Highest (new)** |
| **Fallback Volatility** | semimartingale (Shuai oversight) | Proxy‑source mapping, risk‑based surface‑generation algorithm | Not started | High (new) |
| **Comp Warrant Trading** | Robin (semimartingale algorithm design) | LP vol‑mark estimates, pair‑trading signal generator, execution scripts | Not started | Medium (new) |
| **Asymmetric Spreading** | Ray (Shuai, semimartingale design) | Flow‑aggregation engine, asymmetric‑spread adjustment logic | Not started | High (new) |
| **Gap Risk Hedging** | Ray (semimartingale model development) | Gap‑risk quantification, hedge‑tool selection algorithm | Not started | Medium (new) |

**Total active projects:** 12 (7 existing + 5 new)

## 2. Mapping Personal Objectives to Projects

### Objective 1: P&L & Team Contribution (30 M USD budget)
**Projects that directly contribute:**
- **Warrant Vol Management** – maintain warrant quoting P&L
- **OMM Bricks** – future listed‑option P&L engine
- **Comp Warrant Trading** – arbitrage P&L from warrant pairs
- **Asymmetric Spreading** – reduce adverse‑selection losses
- **Gap Risk Hedging** – reduce CBBC overnight losses

**Personal contribution:** Daily trading routines, risk‑taking decisions, team‑level P&L ownership.

### Objective 2: Own OMM Production & System Rebuild
**Primary project:** **OMM Bricks**
- Spread model, flow model, slippage model → core of OMM quoting engine
- Integration with existing infrastructure (TREE, ETDA)

**Supporting projects:**
- **Stamp Exemption** – reduce transaction costs for OMM trades
- **Algo Vol Fitter** – ensure high‑quality vol surfaces for OMM pricing

**Personal contribution:** Master end‑to‑end OMM workflow, lead algorithm rebuild.

### Objective 3: Guide Listed‑Option Analytics Development
**Primary project:** **Street Directed Flow** (Frankie’s work)
- Bid‑ask spread analytics
- Volume & liquidity profiling  
- Market‑impact measurement

**Supporting project:** **GED Signal** – global signal alignment (Lydie)

**Personal contribution:** Oversight, guidance, ensure production‑ready deliverables.

### Objective 4: Trading Compliance & Operational Excellence
**Cross‑cutting all projects:**
- Zero mispricing incidents across all trading activities
- Compliance training completion
- Daily checklists adherence

**Personal contribution:** Maintain meticulous trade‑booking, reconciliation practices.

### Objective 5: Build Listed‑Option Backtesting Framework
**New standalone deliverable:** ETDA‑based backtesting framework
- Historical replay with realistic execution assumptions
- P&L attribution (delta, vega, theta, spread)
- Integration with ETDA data pipelines

**Connections:** Supports **OMM Bricks** validation and **Comp Warrant Trading** strategy testing.

**Personal contribution:** Design, implementation, team training.

### Objective 6: Sustain Quant Expertise on GED Projects
**Primary projects:** **Algo Vol Fitter**, **Pricing Service**
- Maintain calibration quality
- Support regional migrations (EMEA, US)
- Bridge trading intuition ↔ quant‑dev implementation

**Personal contribution:** Quantitative leadership, problem‑solving, documentation.

### Objective 7: Drive AP Deliveries with Team Review
**Applies to all AP‑focused projects:**
- **Warrant Vol Management** (Robin/Ray review)
- **Stamp Exemption** (Ray review)
- **Elastic** (Ray review)
- **Asymmetric Spreading** (Ray/Shuai review)
- **Gap Risk Hedging** (Ray review)

**Personal contribution:** Weekly syncs, feedback incorporation, clear documentation.

## 3. Timeline Alignment (2026)

### Q1 2026 (Mar‑May)
| Personal Objective | Project Alignment | Milestone |
|-------------------|-------------------|-----------|
| OMM ownership | OMM Bricks design | Finalize spread/flow/slippage model specs |
| Guide Frankie | Street Directed Flow | First analytics brick deployed |
| Sustain GED expertise | Algo Vol Fitter | EMEA migration complete |
| Compliance | All projects | Complete all required trainings |

### Q2 2026 (Jun‑Aug)
| Personal Objective | Project Alignment | Milestone |
|-------------------|-------------------|-----------|
| OMM ownership | OMM Bricks integration | Pilot OMM quoting for 1‑2 underlyings |
| Backtesting framework | ETDA backtesting | First version ready for team use |
| P&L contribution | Asymmetric Spreading | Live test on CBBCs |
| Team integration | All projects | Regularly included in core trading discussions |

### Q3 2026 (Sep‑Nov)
| Personal Objective | Project Alignment | Milestone |
|-------------------|-------------------|-----------|
| OMM ownership | OMM Bricks scale | Expand to 10+ underlyings |
| Guide Frankie | Street Directed Flow | All three analytics bricks production‑ready |
| P&L contribution | Comp Warrant Trading | Live arbitrage on 3‑4 issuer pairs |
| Sustain GED expertise | Pricing Service | US migration complete |

### Q4 2026 (Dec‑Feb 2027)
| Personal Objective | Project Alignment | Milestone |
|-------------------|-------------------|-----------|
| OMM ownership | Full OMM production | Run live OMM book independently |
| P&L contribution | Team 30 M USD budget | Measurable contribution achieved |
| Backtesting framework | Team adoption | Traders run ≥1 backtest per month |
| Success metrics | All objectives | Year‑end review with Shuai/Vassili |

## 4. Success Metrics Alignment

| Personal Success Metric | Project‑Level Metric | Measurement |
|------------------------|----------------------|-------------|
| **Contribute to 30 M USD P&L** | Desk‑level P&L tracking | Monthly P&L attribution |
| **OMM ownership** | OMM Bricks deployment coverage | ≥80% of listed‑option underlyings |
| **Analytics delivery** | Street Directed Flow production‑ready | All three bricks used by traders |
| **Backtesting framework adoption** | ETDA backtesting usage | ≥1 strategy backtest per month by team |
| **Zero compliance incidents** | Cross‑project compliance audit | No mispricing, no rule violations |
| **GED project stability** | Algo Vol Fitter/Pricing Service uptime | ≥99.9% availability, zero major issues |
| **Team integration** | Inclusion in core discussions | Weekly participation in trading huddles |

## 5. Risk Mitigation & Dependencies

### Key Dependencies
1. **Frankie’s capacity** – Street Directed Flow progress depends on his bandwidth.
2. **QuantDev resources** – Algo Vol Fitter/Pricing Service migrations require Matt’s team.
3. **Shuai’s mentorship** – OMM ownership requires his hands‑on trading training.
4. **Ray’s collaboration** – Asymmetric Spreading and Gap Risk Hedging need his trading expertise.

### Mitigation Strategies
- **Weekly syncs** with Frankie to monitor progress.
- **Bi‑weekly GED project reviews** with Matt’s team.
- **Shadow sessions** with Shuai/Ray to accelerate trading intuition.
- **Clear documentation** to ensure knowledge transfer.

## 6. Governance & Reporting

### Weekly Cadence
- **Monday:** Trading team huddle (P&L review, week ahead)
- **Tuesday:** Frankie sync (Street Directed Flow)
- **Wednesday:** GED project review (Algo Vol Fitter/Pricing Service)
- **Thursday:** Shuai 1:1 (OMM progress, trading mentorship)
- **Friday:** Project‑sync with Robin/Ray (AP deliveries)

### Monthly Cadence  
- **Month‑end:** P&L contribution review with Shuai
- **Project milestone review** with Vassili (as needed)

### Quarterly Cadence
- **Q‑end:** Objectives review and adjustment
- **Project roadmap update** based on market conditions

---

## 7. Summary: One‑Page Dashboard

**Personal Focus Areas (2026):**
1. **OMM Production Ownership** – build, deploy, and run listed‑option market‑making engine.
2. **P&L Contribution** – directly impact desk’s 30 M USD budget via multiple projects.
3. **Analytics Leadership** – guide Frankie to deliver production‑ready listed‑option bricks.
4. **Quant Expertise Retention** – maintain GED project stability across regions.
5. **Team Integration** – become embedded core member of PDT APAC trading team.

**Project Portfolio Weighting:**
- **OMM‑centric:** 40% (OMM Bricks, Backtesting Framework)
- **P&L‑centric:** 30% (Warrant Vol Management, Comp Warrant Trading, Asymmetric Spreading)
- **Analytics‑centric:** 20% (Street Directed Flow, GED Signal)
- **GED‑centric:** 10% (Algo Vol Fitter, Pricing Service)

**Success Definition (Dec 2026):**  
*“semimartingale is the go‑to OMM trader, contributes measurably to desk P&L, and has successfully transitioned from quant‑project driver to integrated trading‑team member.”*

---

*This mapping will be reviewed quarterly with Shuai and updated as projects evolve.*