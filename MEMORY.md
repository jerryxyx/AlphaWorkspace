# MEMORY.md – Long-Term Curated Memory

*This file contains distilled wisdom, key decisions, and operational patterns worth preserving across sessions. Updated periodically from daily logs.*

---

## 2026‑03‑11 · Performance & Workflow Optimizations

### Key Learnings (Timeout & Token Consumption)
**Root causes of timeouts:**
1. **Browser automation stuck in ad‑tech frames** – AAStocks, investing.com load dozens of ad iframes; `act/evaluate` waits for all, causing indefinite hangs.
2. **Tavily‑search variable latency** – Some queries >30s; no client‑side timeout control.
3. **Sequential workflow** – Calendar → indices → ADRs → rates → FX → news; any slow step blocks entire report.

**Token‑burn culprits:**
- **Verbose prompts** – Template + instructions + Tavily results added ~10‑15k tokens before real work.
- **Browser snapshots** – Ad‑tech frames alone contributed ~70k tokens in one timed‑out subagent.

### Implemented Fixes
- **Browser timeouts:** Added `timeoutMs: 15000` to all `browser act` calls.
- **Batched Tavily queries:** Combine related searches (calendar, indices, rates/FX, news).
- **Cron‑job payload rewritten:** Concise instructions, explicit timeout guidance.
- **Fallback strategy:** If AAStocks times out, use Tavily for ADR data.
- **Token reduction:** Removed verbose instructional text from payload.

### Data‑Source Decisions
- **ADR excess moves:** Use AAStocks ADR page (`/en/usq/quote/adr.aspx`) with formula:
  ```
  Excess = (ADR_Price_HKD – HK_Price) / HK_Price × 100%
  ```
- **Ex‑dividend dates:** Use AAStocks Corporate Events Dividend (`calendar.aspx?type=5`).
  - **Rule:** Show ex‑div within 1 week ahead (exclude yesterday/before) + next upcoming (even if >1 month).
  - **Note:** AAStocks page may be incomplete (HSBC ex‑div not listed); consider supplemental search.

### Morning‑Report Template Updates
- **Indices table:** `4pm Close (Mark)`, `T‑1 (Day‑on‑Day)`, `T0 (Close‑to‑Present)`.
- **ADR table:** 4‑digit HK symbols, excess calculated via raw prices.
- **Calendar section:** Prioritize AAStocks Corporate Events, fallback to Tavily for missing dividends.

---

## Operational Patterns

### Memory Architecture
- **Daily logs:** `memory/daily/YYYY‑MM‑DD.md` – raw chronological entries.
- **Working buffer:** `SESSION‑STATE.md` – active WAL (Write‑Ahead Log) for current session.
- **Long‑term memory:** `MEMORY.md` (this file) – curated, distilled learnings.

### Morning‑Report Automation
- **Cron job ID:** `f8b26e5c‑dc51‑4da1‑bb86‑8503cf4fb662`
- **Schedule:** 07:00 HKT daily (`0 7 * * *`, Asia/Hong_Kong)
- **Timeout:** 600 seconds (10 minutes)
- **Delivery:** Discord user ID `406062873169887273` (channel `1479543957376471060`)

### ADR Excess‑Move Formula
**Correct calculation:**
```
Excess = (ADR_Price_HKD – HK_Price) / HK_Price × 100%
```
Positive excess → HK price expected to rise relative to ADR; negative → expected to fall.

**Relationship to AAStocks “H Shares VS. ADRs” column:**
- `VS = (HK_Price – ADR_Price_HKD) / ADR_Price_HKD × 100%`
- `Excess ≈ –VS` (differs slightly because `VS` uses ADR price as denominator)

### HK Stock Symbol Formatting
- **Display as 4‑digit codes:** `xxxx.HK` (e.g., `9988.HK`, `0005.HK`).
- **Remove leading zeros:** Convert `00005.HK` → `0005.HK`.

### Browser Automation Best Practices
1. **Always set `timeoutMs`** (e.g., `15000`) on `browser act` calls.
2. **Target specific tables** with XPath/selector; avoid waiting for full page load.
3. **Fallback to Tavily** when AAStocks/investing.com time out.
4. **Close unused tabs** to reduce Chrome memory bloat.

### Tavily‑Search Usage
- **API key:** `tvly‑dev‑1VtFdl‑T6byzyXPQEmdUyN6DdhK4Ar6aF5sDhc5oishHXD6PN`
- **Batch queries:** Combine related topics (e.g., “HSI and HSCEI prices today”).
- **Location restrictions:** Gemini embeddings may fail (`400 User location is not supported`); Tavily works globally.

---

## Upcoming Improvements (Pending)
- **Parallel subagents** for independent report sections.
- **Cache static data** (ex‑div dates, rebalancing) to reduce daily search load.
- **Test optimized workflow** with timeouts and batched queries.

---
*Last updated: 2026‑03‑11 22:48 HKT*