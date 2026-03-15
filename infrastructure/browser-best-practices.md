# Browser Automation Best Practices
*Last Updated: 2026‑03‑15 · For OpenClaw agents*

## Core Principle
**Keep context small.** Browser snapshots can explode token usage (50k‑100k+ tokens per page). Use these patterns to stay under the 128k limit.

## Golden Rules

### 1. Always Use `compact:true`
```javascript
// ✅ DO THIS
browser snapshot <targetId> compact=true

// ❌ NOT THIS
browser snapshot <targetId>
```

**Impact:**
- Full snapshot: 20k‑100k+ tokens
- Compact snapshot: 2k‑10k tokens (70‑90% reduction)

### 2. Use `refs="aria"` for Stable References
```javascript
// ✅ Stable across page changes
browser snapshot <targetId> compact=true refs="aria"

// ❌ Role‑based refs can shift
browser snapshot <targetId> compact=true  // defaults to refs="role"
```

**Why:** ARIA refs (`e123`, `e456`) are unique, stable IDs tied to accessibility attributes. Role‑based refs (`button[0]`, `link[2]`) can change with DOM mutations.

### 3. Limit Nesting with `depth`
```javascript
// ✅ Focus on top‑level elements
browser snapshot <targetId> compact=true refs="aria" depth=2

// ❌ Deep nesting adds bloat
browser snapshot <targetId> compact=true  // defaults to depth=10
```

**When to adjust:**
- `depth=1`: Tables, forms, simple layouts
- `depth=2`: Most pages with moderate nesting
- `depth=3+`: Complex UIs with nested components (rare)

## Complete Safe Pattern
```json
{
  "action": "snapshot",
  "targetId": "A10278E2F569E538F3CC3D2DC553E35E",
  "compact": true,
  "refs": "aria",
  "depth": 2
}
```

## Action Best Practices

### Clicks & Typing
```javascript
// Use refs from aria snapshot
browser act <targetId> kind=click ref=e123
browser act <targetId> kind=type ref=e456 text="search term"
```

### Timeouts
```javascript
// Always set timeoutMs (default may hang)
browser act <targetId> kind=click ref=e123 timeoutMs=15000
browser act <targetId> kind=type ref=e456 text="query" timeoutMs=15000
```

**Recommended:** `timeoutMs=15000` (15 seconds) for most actions.

### Waiting
```javascript
// Brief pauses for UI updates
browser act <targetId> kind=wait timeMs=2000
```

## Tab Management

### Open & Close Strategically
```javascript
// Open only when needed
browser open url="https://example.com" profile=openclaw

// Close immediately after use
browser close targetId=<id>
```

**Rule:** Never leave unused tabs open – each consumes memory and can leak into context.

### Profile Selection
- `profile="openclaw"`: Isolated browser (no user logins, clean state)
- `profile="user"`: User's logged‑in browser (requires approval)
- `profile="chrome-relay"`: Browser Relay extension (user must click toolbar icon)

**Default:** Use `profile="openclaw"` unless you need existing cookies/sessions.

## Context Monitoring

### Check Before Browsing
```javascript
/status  // verify context < 50% before starting
```

**Thresholds:**
- **< 50%**: Safe to browse
- **50‑80%**: Use extra caution, close tabs promptly
- **> 80%**: Stop browsing, close all tabs, consider restart

### When Context Explodes
1. **Close all browser tabs** immediately
2. **Run `/status`** to verify reduction
3. **Consider `/restart`** if still >90% (loses conversation history)
4. **Use isolated sub‑agent** for heavy browsing tasks

## Alternative to Browser

### Use `web_fetch` When Possible
```javascript
// For simple content extraction
web_fetch url="https://example.com/article" extractMode=markdown maxChars=5000
```

**When to prefer `web_fetch`:**
- Reading articles, documentation
- Simple data scraping (no JavaScript)
- No interaction needed

**When browser is required:**
- JavaScript‑heavy pages
- Login‑protected areas
- Complex interactions (clicks, forms, dropdowns)

## Anti‑Patterns to Avoid

### ❌ Multiple Snapshots Without Cleanup
```javascript
// BAD: Context doubles with each snapshot
browser snapshot <id>
browser snapshot <id2>
browser snapshot <id3>
```

### ❌ No Timeouts on Actions
```javascript
// BAD: Can hang indefinitely
browser act <id> kind=click ref=e123
```

### ❌ Leaving Tabs Open
```javascript
// BAD: Memory leak + context contamination
browser open url="https://aastocks.com"
// ... work, then forget to close
```

### ❌ Full Snapshots for Simple Tasks
```javascript
// BAD: 50k tokens for a single button
browser snapshot <id>  // no compact
browser act <id> kind=click ref=button[0]
```

## Quick Reference

| Task | Safe Pattern |
|------|--------------|
| **Initial snapshot** | `browser snapshot <id> compact=true refs="aria" depth=2` |
| **Click button** | `browser act <id> kind=click ref=e123 timeoutMs=15000` |
| **Type text** | `browser act <id> kind=type ref=e456 text="query" timeoutMs=15000` |
| **Wait briefly** | `browser act <id> kind=wait timeMs=2000` |
| **Open page** | `browser open url="..." profile=openclaw` |
| **Close tab** | `browser close targetId=<id>` |
| **Check context** | `/status` |

## Emergency Recovery

If you see **"100% context used 274.9k/128k"**:

1. **Immediately close all browser tabs**
   ```javascript
   browser tabs profile=openclaw  // list tabs
   browser close targetId=<id1>
   browser close targetId=<id2>
   // etc.
   ```

2. **Run `/status`** – should drop to 60‑80%

3. **If still high**, consider:
   - `/restart` – fresh session (loses history)
   - Spawn isolated sub‑agent for remaining work
   - Switch to `web_fetch` instead of browser

## Integration with Agent Workflow

### For Morning Reports (AAStocks, etc.)
```javascript
// 1. Open with timeout
browser open url="http://www.aastocks.com/en/usq/quote/adr.aspx" profile=openclaw

// 2. Snapshot compactly
browser snapshot <id> compact=true refs="aria" depth=2

// 3. Extract table data (target specific elements)
// 4. Close immediately
browser close targetId=<id>
```

### For Research (Google Scholar)
```javascript
// 1. Open with US proxy enabled
// 2. Snapshot search box compactly
// 3. Type query with timeout
// 4. Snapshot results (depth=2)
// 5. Extract papers
// 6. Close all tabs
```

## Tool Configuration Notes

- **Default profile**: `openclaw` (clean, isolated)
- **Default refs**: `"role"` (change to `"aria"`)
- **Default depth**: 10 (reduce to 2)
- **Default timeout**: varies (always set explicitly)

**Always override defaults** with the safe patterns above.

---

*This guide is part of the OpenClaw workspace infrastructure. Update as new patterns emerge.*