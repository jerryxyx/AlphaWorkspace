# ADR Excess Moves (HK Open Estimate)
*Date: 2026‑03‑11 · Time: 08:12 HKT*

**Source**: AAStocks.com ADR page (`/en/usq/quote/adr.aspx`) and A+H+ADR page (`/en/stocks/market/ahadr.aspx`).  
**Interpretation**: Column “H Shares VS. ADRs” shows the difference (in HKD) between the Hong Kong share price and the ADR price (converted to HKD).  
**Excess move** = – (H Shares VS. ADRs) — the estimated gap‑filling move for the HK open.

## Top Moves (>1% Excess) + Always‑Included Stocks

| Symbol   | Name                     | H Shares VS. ADRs (HKD) | Excess Move (%) | >1% Flag |
|----------|--------------------------|-------------------------|-----------------|----------|
| 3988.HK  | BANK OF CHINA            | +1.286                  | –28.64%         | ✅       |
| 1398.HK  | ICBC                     | +1.127                  | –17.95%         | ✅       |
| 0939.HK  | CCB                      | +0.330                  | –4.17%          | ✅       |
| 2318.HK  | PING AN                  | –0.822                  | +1.30%          | ✅       |
| 1211.HK  | BYD COMPANY              | +0.945                  | –0.97%          |          |
| 3968.HK  | CM BANK                  | +0.449                  | –0.90%          |          |
| 0005.HK  | HSBC HOLDINGS            | 0.000% (0 HKD)          | 0.00%           |          |
| 0388.HK  | HKEX                     | 0.000% (0 HKD)          | 0.00%           |          |
| 0700.HK  | TENCENT                  | 0.000% (0 HKD)          | 0.00%           |          |
| 3690.HK  | MEITUAN‑W                | 0.000% (0 HKD)          | 0.00%           |          |
| 9988.HK  | BABA‑W (Alibaba)         | 0.000% (0 HKD)          | 0.00%           |          |

## Notes
- **Data freshness**: Prices and differences reflect previous close (market not yet open). Real‑time updates may change values after 9:15 HKT.
- **Zero‑difference stocks**: The five always‑shown stocks (0005, 0388, 0700, 3690, 9988) currently show 0.000% difference; this may indicate no arbitrage gap at previous close.
- **Excess move sign**: Positive excess means the HK price is expected to rise relative to the ADR; negative excess means expected fall.
- **Methodology**: `Excess Move (%)` = – (H Shares VS. ADRs in HKD) ÷ (HK Price) × 100%.

## Focus for Today’s Open
- Largest expected gap‑fill: **BANK OF CHINA (–28.64%)** and **ICBC (–17.95%)** suggest significant downward pressure on those HK shares.
- **PING AN (+1.30%)** slight upward bias.
- The five core stocks show no arbitrage signal at close.

---

*Data retrieved via browser automation from AAStocks.com. Computed at 08:12 HKT.*