# Weekly Review Checklist
*Part of the Agent Programme’s structured‑memory system*

This checklist guides the weekly review of the Agent Programme, roles, and knowledge.

## 1. Programme Document
- [ ] Open `PROGRAMME.md` and read through the entire digested version.
- [ ] Compare with raw original (`programme/raw/AgentProgramme.txt`) for any discrepancies.
- [ ] Note any sections that feel outdated, incomplete, or misaligned with current practice.
- [ ] Propose updates (edits, additions, clarifications) and discuss with the Operator.
- [ ] Once agreed, update `PROGRAMME.md` and commit with message `weekly: programme updates`.

## 2. Roles Report
### 2.1 Trading Execution
- [ ] Review `roles/trading‑execution/topics/` for new market summaries, decision trees, workflows.
- [ ] Check `roles/trading‑execution/delivery/` for new/updated scripts, dashboards, logs.
- [ ] Assess whether execution‑role knowledge is keeping pace with market developments.

### 2.2 Trading Project
- [ ] Review `roles/trading‑project/topics/` for quantitative research, models, math notes.
- [ ] Check `roles/trading‑project/delivery/` for code, backtests, visualizations.
- [ ] Evaluate project‑role progress against quarterly/annual goals.

## 3. Knowledge Report
### 3.1 Update `knowledge/INDEX.md`
- [ ] Scan all `topics/` and `delivery/` folders across the workspace for new files.
- [ ] For each new file, add an appropriate entry to `knowledge/INDEX.md`.
- [ ] Remove entries for files that have been deleted or archived.
- [ ] Ensure all links in the index are correct (relative paths work).

### 3.2 Review Knowledge Domains
- [ ] **Trading knowledge**: Verify product specs, market mechanics, risk concepts are current.
- [ ] **Quantitative knowledge**: Check models, formulas, derivations for accuracy.
- [ ] **Operational knowledge**: Update tool/process documentation as needed.

### 3.3 Audit Memory Logs
- [ ] Read through the past week’s daily logs (`memory/daily/`).
- [ ] Identify patterns, lessons, or decisions worth promoting to long‑term memory.
- [ ] Write a weekly summary in `memory/weekly/YYYY‑MM‑DD‑summary.md`.
- [ ] Optionally, curate key insights into `memory/long‑term/` or `MEMORY.md` (main‑session).

## 4. Git Commit & Tag
- [ ] Stage all changes: `git add .`
- [ ] Commit with message: `weekly: review YYYY‑MM‑DD`
- [ ] Tag the commit: `git tag -a week‑YYYY‑MM‑DD -m \"Weekly review\"`
- [ ] Push to remote repository (if configured).

## 5. Schedule Next Review
- [ ] Confirm the cron job for next Sunday is active (`openclaw cron list`).
- [ ] Adjust timing if needed (e.g., holiday, travel).

---

*This checklist is a living document. Update it as the review process evolves.*