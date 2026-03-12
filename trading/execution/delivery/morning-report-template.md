# Morning Trading Report
*Date: {{date}} · Time: 07:00 HKT*

## 1. Calendar Events (Next 2 Weeks)

### Ex‑dividend Dates (HKEX Listed Equity)
| Date | Stock (Symbol) | Div Amount (HK$) | Div % | Payable Date | Note |
|------|----------------|------------------|-------|--------------|------|
| *Search HKEX announcements for ex‑dividend dates in next 14 days* | | | | | |

*Example:*
| 2026‑03‑12 | HSBC (0005.HK) | 3.53 | 2.60% | 2026‑04‑30 | Quarterly dividend |
| 2026‑03‑11 | HKEX (0388.HK) | 6.52 | *tbd* | 2026‑03‑25 | Second interim dividend |

### Index Rebalancing (Next 2 Weeks)
- *HSI, HSCEI, Hang Seng Tech Index rebalancing dates if within 2 weeks*

### Major Macro Releases (China Only)
- *List China macro releases with precise scheduled times*

## 2. Overnight Spot Moves

### Hong Kong Indices (Overnight Moves)
| Index | 4pm Close (Mark) | T‑1 (Day‑on‑Day) | T0 (Close‑to‑Present) |
|-------|------------------|------------------|----------------------|
| HSI | | | |
| HSCEI | | | |

*4pm Close (Mark): Yesterday's close (most recent trading day).  
T‑1: Day‑on‑day change from previous close to yesterday's close.  
T0: Close‑to‑present move from yesterday's close to current live spot (Yahoo Finance/Reuters).*

### Major ADRs/GDRs (AAStocks.com)
| Stock (Symbol) | Last Close | Current | Change | % Change | Note |
|----------------|------------|---------|--------|----------|------|
| *Big names / big moves only. Symbols as 4‑digit codes (e.g., 3988.HK, 1398.HK).*  
*Excess move (expected HK open gap‑fill) = (ADR_Price_HKD – HK_Price) / HK_Price × 100%.* | | | | | |

### Interest Rate Moves (Pre‑9:15am Proxy)
**US Treasury Yields (3M, 6M, 1Y, 2Y)**
- Current yields and overnight change
- 5‑day trend (values for past 5 consecutive days)

**Hong Kong IRSB Rates** (if available before 9:15am)
- Current IRSB benchmarks (3M, 6M, 1Y, 2Y)
- Daily change vs yesterday
- 5‑day trend vs US moves alignment

*Note: Hong Kong rates released at ~9:15 HKT; pre‑open proxy is US rate movement.*

### FX Rates
| Pair | Current | 1D Change | 5D Change |
|------|---------|-----------|-----------|
| USD/HKD | | | |
| HKD/CNY | | | |

## 3. News & Sentiment (HKEX Stocks & Macro)
- **HKEX Stocks (.HK)**: *Company‑specific news*
- **Macro Developments**: *China/HK policy, economic data*
- **Sector Themes**: *Notable sector movements*

## 4. Volatility Conduction
- **9:15 HSI stock‑vol open**: *Previous close vol: __.*
- **9:30 option market open**: *Anticipate early flow based on overnight moves.*
- **Spot movement at 9:15/9:20**: *Adjust spreads if spot gap > 0.5%.*

## 5. Desk‑Specific Parameters
### Pricing Engine
- **UsedVol** = ManVol(editable) + ManVolTraderOffset(editable) + ManVolOffset(algo) + AdjVol(algo)
- **DeltaSpreadBid/Ask**: *Default settings.*
- **Tick/Cash spread**: *Trader‑tweakable.*

### KO (CBBC) Preparedness
- **CBBCs near barrier** (< 3% spot move): *None identified.*
- **Overnight gap risk**: *Review positions after open.*

## 6. Dashboard Metrics (Previous Day)
- **P&L**: *Not available.*
- **Delta/Vega/Gamma**: *Not available.*
- **SlippageProduct**: *Not available.*
- **SlippageHedge**: *Not available.*

## 7. Today’s Focus
- Monitor early vol conduction (9:15–9:30).
- Adjust margins/spreads based on spot moves.
- Watch for KO events in CBBCs.
- Note interest rate alignment between HK and US.

---

*This is an automated report based on the updated checklist. Data sourced via Tavily search.*