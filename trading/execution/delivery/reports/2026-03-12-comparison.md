# Proxy vs. Direct Comparison
*Morning Trading Report – 2026‑03‑12*

## Performance
| Metric | Proxy (US) | Direct (HK) |
|--------|------------|-------------|
| Avg Tavily query latency | 4.5‑4.8 s | 4.3‑4.8 s |
| Total report generation time | ~5 min | ~5 min |
| API availability | Full access | Full access |
| Geo‑restriction observed | None | None |

## Data Differences
### 1. ADR Prices (Critical Difference)
| Stock | Proxy (US IP) | Direct (HK IP) | Impact |
|-------|---------------|----------------|--------|
| Tencent ADR | $71.16 (‑3.79%) | $73.96 (+10.39%) | **Large discrepancy** – proxy gave Mar 11 close; direct gave Mar 10 close. |
| Alibaba ADR | $136.29 (‑0.41%) | 22,060.00 (‑0.81%) | **Major error** – direct search returned mis‑parsed value (likely a different ticker). |
| Tencent HK | HK$552.00 | HK$552.00 | Same |
| Alibaba HK | HK$133.20 | HK$133.20 | Same |

**ADR‑implied excess moves:**
- **Proxy**: Tencent +0.85%, Alibaba +0.08%
- **Direct**: Tencent +4.83%, Alibaba +0.08% (using correct ADR price $136.29)

### 2. US Treasury Yields
| Maturity | Proxy | Direct |
|----------|-------|--------|
| 3M | 3.69% | 3.69% |
| 6M | 3.67% | 3.67% |
| 1Y | – | 3.60% |
| 2Y | 3.69% | 3.69% |

*Direct provided 1‑year yield; proxy omitted it.*

### 3. FX Rates
| Pair | Proxy | Direct |
|------|-------|--------|
| USD/HKD | 7.8242 | 7.82 |
| HKD/CNY | 0.8770 | 0.88 |

*Minor rounding differences.*

### 4. News & Sentiment
- Both reported HSI fell 0.24% on Mar 11, Middle East concerns.
- Both cited China GDP target 4.5‑5% for 2026.
- Sources overlapped (SCMP, Trading Economics) but proxy included more US‑centric outlets (Wise, Investing.com), direct included more local (Yahoo Finance HK).

## Quality Assessment
- **Proxy (US)** – More consistent ADR pricing (correct date), cleaner numeric extraction.
- **Direct (HK)** – Introduced errors in ADR parsing (Alibaba), picked older date for Tencent ADR.
- **HK‑listed prices** – Identical across both.
- **Macro data** – Similar; proxy slightly more complete.

## Operational Implications
1. **ADR data quality** – Proxy (US) yields more reliable ADR quotes for HK‑listed stocks.
2. **Latency** – Negligible difference; proxy adds no meaningful overhead.
3. **Source bias** – US IP may favor Western financial sites (Investing.com, Wise); HK IP may favor local sources (Yahoo Finance HK, SCMP).
4. **Error rate** – Direct search produced one blatant error (Alibaba ADR 22,060). This could mislead trading decisions.

## Recommendation
**Use proxy (non‑HK IP) for morning‑report generation** when ADR data is critical. The VPN toolkit (`infrastructure/vpn/delivery/clash_fastest_non_hk.py`) can auto‑select the fastest US proxy with `--switch`.

**Fallback**: If proxy fails, revert to DIRECT but validate ADR numbers manually.

## Files
- Proxy‑on report: `2026‑03‑12‑proxy.md`
- Direct report: `2026‑03‑12‑direct.md`
- This comparison: `2026‑03‑12‑comparison.md`

*All reports saved in `/Users/xyx/.openclaw/workspace/trading/execution/delivery/reports/`.*