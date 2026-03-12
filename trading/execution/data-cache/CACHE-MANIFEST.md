# Data Cache Manifest
*For Morning Trading Report efficiency*

## Purpose
Reduce Tavily search costs by caching frequently‑accessed data with reasonable expiration times.

## Cache Files

### `ex‑dividend‑cache.json`
- **Contents**: Upcoming ex‑dividend dates for HKEX stocks (next 30 days)
- **Update frequency**: Weekly (Sunday 22:00 HKT)
- **Schema**:
```json
{
  "lastUpdated": "2026‑03‑11T23:45:00Z",
  "expiresAt": "2026‑03‑18T22:00:00Z",
  "data": [
    {
      "date": "2026‑03‑12",
      "symbol": "0005.HK",
      "name": "HSBC Holdings",
      "divAmountHKD": 3.53,
      "divPercent": 2.6,
      "payableDate": "2026‑04‑30",
      "note": "Quarterly dividend"
    }
  ]
}
```

### `adr‑ratios‑cache.json`
- **Contents**: ADR‑to‑HK share conversion ratios for major stocks
- **Update frequency**: Monthly (1st of month)
- **Schema**: List of {symbol, adrSymbol, ratio, lastVerified}

### `index‑levels‑cache.json`
- **Contents**: Previous close levels for HSI, HSCEI
- **Update frequency**: Daily (after market close)
- **Schema**: {date, hsiClose, hsceiClose, timestamp}

## Usage in Report Generation
1. Check if cache exists and is not expired
2. If valid, use cached data
3. If missing/expired, perform Tavily search and update cache
4. Log cache hits/misses in report‑generation‑log.md

## Maintenance
- Cache files are git‑ignored (add to `.gitignore`)
- Manual override: delete cache file to force refresh
- Size control: prune entries older than 30 days