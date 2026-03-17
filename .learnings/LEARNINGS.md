# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice
**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted | promoted_to_skill

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Issue fixed or knowledge integrated |
| `wont_fix` | Decided not to address (reason in Resolution) |
| `promoted` | Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md |
| `promoted_to_skill` | Extracted as a reusable skill |

## Skill Extraction Fields

When a learning is promoted to a skill, add these fields:

```markdown
**Status**: promoted_to_skill
**Skill-Path**: skills/skill-name
```

Example:
```markdown
## [LRN-20250115-001] best_practice

**Logged**: 2025-01-15T10:00:00Z
**Priority**: high
**Status**: promoted_to_skill
**Skill-Path**: skills/docker-m1-fixes
**Area**: infra

### Summary
Docker build fails on Apple Silicon due to platform mismatch
...
```

## [LRN-20260317-001] best_practice

**Logged**: 2026-03-17T04:56:13Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Always add `timeoutMs: 15000` to `browser act` calls to avoid indefinite hangs in morning‑report automation.

### Details
Morning‑report generation frequently timed out because browser automation (`browser act`) would wait indefinitely for ad‑tech iframes on AAStocks/investing.com pages. Root cause: `act/evaluate` waits for all frames, including slow third‑party ads. Adding explicit `timeoutMs: 15000` (15 seconds) ensures the call fails fast, allowing fallback to Tavily search.

### Suggested Action
1. Always include `timeoutMs: 15000` (or appropriate value) in `browser` tool calls.
2. Implement fallback logic: if browser times out, use Tavily/web search for data.
3. Log timeouts to `memory/network‑timeouts.log` for monitoring.

### Metadata
- Source: timeout_optimization
- Related Files: `MEMORY.md` (2026‑03‑11 entry), `SESSION‑STATE.md`
- Tags: browser, timeout, automation, morning‑report
- Pattern‑Key: timeout.browser_act
- Recurrence‑Count: 1
- First‑Seen: 2026‑03‑11
- Last‑Seen: 2026‑03‑17

---

## [LRN-20260317-002] best_practice

**Logged**: 2026-03-17T12:11:50Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Always use `compact=true`, `refs="aria"`, `depth=2` in browser snapshots to reduce context token usage by 70‑90%.

### Details
Browser snapshots can explode token consumption (50k‑100k+ tokens per page) due to full DOM trees, ad‑tech iframes, and deep nesting. The default snapshot (`compact=false`, `refs="role"`, `depth=10`) captures excessive detail that bloats context windows and can cause timeouts. Applying compact snapshot patterns reduces token usage dramatically while preserving actionable UI references.

### Suggested Action
1. **Always add `compact=true`** to `browser snapshot` calls.
2. **Prefer `refs="aria"`** for stable element IDs (`e123`) over role‑based refs (`button[0]`) that shift with DOM mutations.
3. **Limit `depth=2`** for most pages, `depth=1` for tables/forms.
4. **Combine with `timeoutMs: 15000`** on `browser act` calls to prevent indefinite hangs.
5. **Close unused tabs** immediately to avoid memory/context leaks.

### Metadata
- Source: browser_optimization
- Related Files: `infrastructure/browser‑best‑practices.md`, `MEMORY.md`
- Tags: browser, snapshot, compact, tokens, context
- Pattern‑Key: browser.snapshot_compact
- Recurrence‑Count: 1
- First‑Seen: 2026‑03‑17
- Last‑Seen: 2026‑03‑17

---

## [LRN-20260317-003] best_practice

**Logged**: 2026-03-17T12:34:38Z
**Priority**: high
**Status**: pending
**Area**: workflow

### Summary
Break big tasks into independent subtasks, execute via parallel subagents, then combine results (map‑reduce pattern).

### Details
Large requests often contain multiple independent components that can be executed in parallel rather than sequentially. Example: morning report has 6 independent sections (calendar, indices, ADRs, rates, FX, news). Running sequentially creates single‑point failures and long runtimes. Spawning parallel subagents isolates token usage, prevents context‑window bloat, enables fault tolerance, and reduces total runtime through concurrency.

### Suggested Action
1. **Analyze request** for independent subtasks.
2. **Spawn subagents** for each parallelizable component.
3. **Set appropriate timeouts** (`runTimeoutSeconds: 600` for long tasks).
4. **Wait for all subagents** to complete.
5. **Combine outputs** into final conclusion.
6. **Apply compact browser patterns** (`compact=true`, `timeoutMs: 15000`) within each subagent.

### Metadata
- Source: subagent_orchestration
- Related Files: `AGENTS.md` (new section), `MEMORY.md`
- Tags: subagent, parallel, orchestration, map‑reduce, workflow
- Pattern‑Key: workflow.parallel_subagents
- Recurrence‑Count: 1
- First‑Seen: 2026‑03‑17
- Last‑Seen: 2026‑03‑17

---

