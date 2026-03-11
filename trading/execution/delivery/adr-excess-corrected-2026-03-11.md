# ADR Excess Moves – Corrected Calculation
*Date: 2026‑03‑11 · Time: 11:10 HKT*

**Source:** AAStocks.com ADR page (`/en/usq/quote/adr.aspx`), table “H Shares VS. ADRs”.

## Formula Clarification

1. **Column “H Shares VS. ADRs”** (denoted `VS`) is already a **percentage**:
   ```
   VS = (HK_Price – ADR_Price_HKD) / ADR_Price_HKD × 100%
   ```
   Positive `VS` means the HK price is **higher** than the ADR price (in HKD terms).

2. **Excess move** (expected HK price movement to close the gap) should be computed using the **HK price as denominator**:
   ```
   Excess (correct formula) = (ADR_Price_HKD – HK_Price) / HK_Price × 100%
   ```
   Positive excess → HK price expected to **rise** relative to ADR; negative → expected to **fall**.

3. **Relationship to VS column**:
   ```
   Excess = –VS × (ADR_Price_HKD / HK_Price)
   ```
   Because `VS` uses ADR price as denominator, a simple sign reversal (`–VS`) yields a slightly different magnitude. For consistency, always compute excess using raw prices (HK and ADR HKD).

## Comparison Table

| Symbol   | Name               | HK Price (HKD) | ADR Price (HKD) | VS ADR (%) | Excess (‑VS) | Manual Excess | Difference |
|----------|--------------------|----------------|-----------------|------------|--------------|---------------|------------|
| 0175.HK  | GEELY AUTO 1       | 17.62          | 19.11           | –7.799%    | **7.799%**   | 8.456%        | –0.657%    |
| 0027.HK  | GALAXY ENT 5       | 37.74          | 40.28           | –6.302%    | **6.302%**   | 6.728%        | –0.426%    |
| 0002.HK  | CLP HOLDINGS       | 73.50          | 75.66           | –2.854%    | **2.854%**   | 2.937%        | –0.083%    |
| 0101.HK  | HANG LUNG PPT 2    | 9.14           | 9.40            | –2.813%    | **2.813%**   | 2.899%        | –0.086%    |
| 0006.HK  | POWER ASSETS       | 62.80          | 61.19           | +2.640%    | **–2.640%**  | –2.572%       | –0.068%    |
| 0005.HK  | HSBC HOLDINGS 4    | 135.50         | 134.32          | +0.875%    | **–0.875%**  | –0.868%       | –0.007%    |
| 0388.HK  | HKEX 7             | 412.60         | –               | –          | –            | –             | –          |
| 0700.HK  | TENCENT 9          | 566.00         | 578.67          | –2.190%    | **2.190%**   | 2.239%        | –0.049%    |
| 3690.HK  | MEITUAN‑W 1        | 78.00          | –               | –          | –            | –             | –          |
| 9988.HK  | BABA‑W 7           | 135.40         | –               | –          | –            | –             | –          |

**Notes:**

- **Excess (‑VS)** is the figure that should be used for HK‑open estimates (sign reversal of the published column).
- **Manual Excess** differs because it uses HK price as denominator instead of ADR price. The difference is usually small (<0.7%).
- **VS ADR** negative → HK price lower than ADR → HK expected to rise (positive excess).
- **VS ADR** positive → HK price higher than ADR → HK expected to fall (negative excess).
- Stocks with no ADR data (0388.HK, 3690.HK) have no arbitrage signal in this dataset.

## Top 5 Excess Moves (>1% absolute)

1. **GEELY AUTO (0175.HK)** +7.80% (ADR priced 8.5% above HK)
2. **GALAXY ENT (0027.HK)** +6.30%
3. **CLP HOLDINGS (0002.HK)** +2.85%
4. **HANG LUNG PPT (0101.HK)** +2.81%
5. **POWER ASSETS (0006.HK)** –2.64%

## Always‑Included Stocks (0005, 0388, 0700, 3690, 9988)

- **0005.HK** HSBC: slight negative excess (–0.88%).
- **0388.HK** HKEX: no ADR data.
- **0700.HK** Tencent: +2.19% excess (ADR priced 2.2% above HK).
- **3690.HK** Meituan‑W: no ADR data.
- **9988.HK** BABA‑W: no ADR data in this table.

## Recommendation

Use **Excess (‑VS)** for consistency with AAStocks’ published column. For data vendors that do not provide the “H Shares VS. ADRs” field, compute **Manual Excess** using raw ADR‑HKD and HK‑HKD prices; the directional signal will be the same, magnitude slightly different.

---

*Data retrieved via browser automation at 11:10 HKT. Symbols shown as 4‑digit HK codes.*