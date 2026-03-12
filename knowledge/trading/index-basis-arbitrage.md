# Index Basis Arbitrage
*Last Updated: 2026‑03‑12 · Source: Discussion with semimartingale*

## Overview
Index basis arbitrage is a market‑neutral strategy that exploits temporary mispricings between a stock‑index futures contract and its underlying cash basket. The primary participants are **bank proprietary‑trading desks** with large inventories of the index constituents, giving them a structural cost advantage (stamp‑duty exemption) that makes the business viable.

## Key Concepts

### Fair‑Value Formula
The theoretical price of a futures contract is given by the **cost‑of‑carry** model:

```
F = S × e^{(r − q) × T}
```

**Linear approximation (small (r‑q)×T):**
```
F ≈ S × [1 + (r − q) × T]
```

Where:
- **S** = Spot index level (published cash index, e.g., HSI)
- **r** = Risk‑free financing rate (HIBOR for HKD‑denominated indices)
- **q** = Dividend yield of the index basket (annualized)
- **T** = Time to expiry (in years)

The **fair basis** is:
```
Basis_fair = S × (r − q) × T
```

### Market Basis
```
Basis_market = Futures_price − Spot
```

**Arbitrage opportunity exists when:**
- `Basis_market > Basis_fair` → futures are **rich** → **cash‑and‑carry** trade (buy basket, sell futures).
- `Basis_market < Basis_fair` → futures are **cheap** → **reverse cash‑and‑carry** trade (short basket, buy futures).

## Trade Lifecycle

### 1. Opportunity Identification
- Monitor real‑time spot index (published every 2 seconds by HKEX) and front‑month futures price.
- Compute fair basis using current HIBOR and dividend‑yield forecasts.
- Trigger when `|Basis_market − Basis_fair| > transaction_cost + stamp_duty (if any)`.

### 2. Trade Setup
**Cash‑and‑Carry (futures rich):**
1. Borrow HKD at HIBOR (floating rate).
2. Buy the full basket of index constituents (or a tight ETF like 2800.HK).
3. Sell front‑month futures contracts.
4. *Stamp‑duty cost*: 0.13% on purchase (avoided if using internal inventory).

**Reverse Cash‑and‑Carry (futures cheap):**
1. Borrow the basket (via stock‑loan desk) and sell it short.
2. Use sale proceeds to buy front‑month futures.
3. Pay stock‑loan fee (and any dividend payments).

### 3. Holding Period
- **Daily carry**: Financing cost (HIBOR) − dividends received.
- **Mark‑to‑market**: Futures position revalued daily; margin calls if basis widens.
- **Monitoring**: Watch for convergence, HIBOR moves, dividend surprises.

### 4. Unwind
- **Hold to expiry**: Futures settle to the special opening quotation (SOQ) of the spot index; basket sold/delivered simultaneously.
- **Early close**: If basis converges before expiry, close both legs to realize P&L earlier.

## P&L Drivers & Sensitivity

### Base Case Example (30‑day cash‑and‑carry)
| Component | Points (S = 25,900) |
|-----------|----------------------|
| Locked‑in richness (Basis_market − Basis_fair) | +10.0 |
| Financing cost (4.00% p.a.) | −85.2 |
| Dividends earned (3.00% p.a.) | +63.9 |
| Transaction cost (slippage, fees) | −1.0 |
| Stamp duty (0.13% per leg) | −33.7 (if paid) |
| **Net P&L (with stamp duty)** | **‑24.7** (loss) |
| **Net P&L (no stamp duty)** | **+9.0** (profit) |

### HIBOR Sensitivity
A **50 bps increase** in HIBOR mid‑trade:
- Increases financing cost by **~5.3 points** over 30 days.
- Reduces profit by **5.3 points** (≈59% of base profit).
- Futures fair‑value basis expands by `S × Δr × T ≈ +10.6 points`, causing a mark‑to‑market loss on short futures position (reversed at expiry).

**Why the trade is *short funding*:** It borrows cash at a floating rate; rising HIBOR directly reduces P&L.

### Stamp‑Duty Impact
- **Round‑turn cost**: 0.26% of notional (0.13% buy + 0.13% sell) = **~67.4 points** on HSI 25,900.
- **Bank advantage**: Internal inventory transfers avoid stamp duty, turning a loss‑making trade for external players into a profitable one.

## Structural Advantages of Banks

| Advantage | How it works | Economic Benefit |
|-----------|--------------|------------------|
| **Internal inventory** | Borrow basket from inventory desk; no market purchase → no stamp duty. | +34 points per leg (≈1.3% of notional). |
| **Cheaper funding** | Access to HIBOR flat via internal treasury (vs. HIBOR + 30‑50 bps for external). | +0.3‑0.5% annualized. |
| **Stock‑loan rebates** | Lend out hard‑to‑borrow names from inventory, earning 10‑50 bps p.a. | +0.1‑0.5% annualized. |
| **Scale & automation** | DMA/VWAP algos, low per‑unit transaction costs. | +0.5‑2 points per round‑turn. |
| **Regulatory netting** | Lower Basel‑III risk‑weighting for internal exposures. | Lower capital charge. |

## Market Impact & Desk Behavior

### Duration of Mispricing
- **Arb‑desk flow**: Minutes to an hour (their block trade moves price; other arbs converge quickly).
- **Model‑data staleness**: Whole day (if HIBOR/dividend inputs are not updated intraday).
- **Liquidity drought**: 30 min – 2 hours (few participants to correct).
- **Corporate‑action news**: Hours – until next trading day (market prices in immediately; model lags).

### Intraday Pattern (HSI Futures)
- **9:15‑9:30**: Large, fast‑moving mismatches (overnight ADR gaps, opening hedge flow).
- **9:30‑11:00**: Rapid convergence (high liquidity, multiple arb desks active).
- **11:00‑15:00**: Stable, tight basis (< 5 points).
- **15:00‑16:00**: Mismatches may reappear (pre‑close hedging).
- **After 16:00**: Basis widens (less liquidity, higher transaction costs).

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| **HIBOR spikes** | Hedge with HIBOR futures (HIF) or forward rate agreements (FRA). |
| **Dividend surprises** | Dynamic dividend‑forecast models, corporate‑action feeds. |
| **Basis divergence** | Stop‑out thresholds, position limits. |
| **Execution slippage** | VWAP algorithms, trade in high‑liquidity windows. |
| **Counterparty default** | Clear through HKCC, use prime‑broker with strong collateral agreement. |
| **Index rebalancing** | Pre‑adjust basket before HKEX announcement. |

## Implications for ULP Pricing

1. **Basis stability**: Banks’ continuous arb activity keeps **implied cash** (futures‑derived) close to **published cash**, reducing pricing mismatch.
2. **Liquidity provision**: When banks are active, futures spreads tighten, making hedging cheaper.
3. **Stamp‑duty pass‑through**: Any physical hedging (buying/selling basket) incurs 0.13% duty – a cost banks avoid.
4. **Model‑vs‑market gaps**: If your marked price uses stale HIBOR/dividend inputs, mismatches can persist all day; update inputs intraday.

## Further Reading
- [Cost‑of‑carry model](https://www.investopedia.com/terms/c/costofcarry.asp)
- [Hong Kong Stamp Duty Ordinance](https://www.elegislation.gov.hk/hk/cap117)
- [HKEX Derivatives Market – HSI Futures](https://www.hkex.com.hk/Products/Derivatives/Equity-Index/Hang-Seng-Index-Futures-and-Options?sc_lang=en)

---
*This knowledge file is part of the OpenClaw workspace’s structured‑memory system. Refer to [INDEX.md](../INDEX.md) for the full domain map.*