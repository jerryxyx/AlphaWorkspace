# Pre‑Market Checklist
*For HK public‑distribution desk (warrants, CBBCs, listed options, DLC)*

Review each morning before market open (∼8:45–9:15 HKT).

## 1. Calendar Events
- [ ] **Ex‑dividend dates** for underlying equities (check HKEX announcements).
- [ ] **Index rebalancing** or special settlement dates.
- [ ] **Major macro releases** (HK, US, China) scheduled for the day.

## 2. Overnight Spot Moves
- [ ] **HSI futures** vs. previous close (% change).
- [ ] **HSCEI futures** vs. previous close.
- [ ] **Major single‑stock ADRs/GDRs** (if applicable).
- [ ] **USD/CNH** and other relevant FX moves.

## 3. News & Sentiment
- [ ] **Headline news** that may cause major spot movement (HK/China policy, corporate actions).
- [ ] **Sector‑specific developments** (property, tech, financials).
- [ ] **Competitor issuer announcements** (new listings, margin changes).

## 4. Volatility Conduction
- [ ] **9:15 HSI stock‑vol open** – note any gap vs. previous close.
- [ ] **9:30 option market open** – anticipate early flow based on vol moves.
- [ ] **Spot movement at 9:15 (HSI) and 9:20 (stocks)** – adjust quoting spreads accordingly.

## 5. Desk‑Specific Parameters
### 5.1 Pricing Engine
- **UsedVol** = ManVol(editable) + ManVolTraderOffset(editable) + ManVolOffset(algo) + AdjVol(algo)
- **DeltaSpreadBid/Ask** (editable)
- **Tick/Cash spread** (trader‑tweakable)

### 5.2 Decision Tree for Adjustments
- **Symmetric move (margin)**: adjust both bid/ask by same amount.
- **Asymmetric move (spreading)**: widen/compress one side more than the other.
- **Trigger**: spot move beyond threshold, vol conduction, news impact.

### 5.3 KO (CBBC) Preparedness
- Identify CBBCs near barrier (< 3% spot move).
- Plan intraday delta adjustment if KO occurs.
- Assess overnight gap risk for CBBCs near barrier at previous close.

## 6. Dashboard Metrics to Monitor at Open
- P&L (overnight vs. intraday)
- Delta/Vega/Gamma per underlying & product type
- SlippageProduct (trade vs. engine mid) from previous day
- SlippageHedge (hedge execution) from previous day
- Recent spot moves, positions

## 7. Communication
- [ ] Brief trading team on key focus areas.
- [ ] Flag any unusual risk concentrations.

---

**Post‑Checklist Actions**
1. Update any engine parameters before 9:15.
2. Monitor first 30 minutes of trading for unexpected flow.
3. Log any deviations from checklist in `memory/daily/YYYY‑MM‑DD.md`.

**Report‑Generation Notes**
- Check `data‑cache/` for stale entries (weekly refresh).
- Update `report‑generation‑log.md` with each execution.
- Prefer cache over Tavily search to reduce costs.
- Validate ex‑dividend % = Div Amount / Previous Close.

---

*This checklist evolves with market structure and desk procedures. Update as needed.*