# Daily Git Routine
*Ensuring version‑control discipline as per the Agent Programme*

## Purpose
Commit workspace changes at the end of each day to:
- Preserve a granular history of knowledge evolution.
- Enable rollback to any prior state.
- Facilitate cloning the knowledge tree to new machines.

## Steps
1. **Check for changes**
   ```bash
   cd /Users/xyx/.openclaw/workspace
   git status
   ```

2. **Review what will be committed**
   - Look at `git diff --staged` (if already staged) or `git diff` (unstaged).
   - Ensure no sensitive data (API keys, personal info) is accidentally included.

3. **Stage changes**
   ```bash
   git add .
   ```
   Or stage selectively:
   ```bash
   git add path/to/specific/files
   ```

4. **Write a meaningful commit message**
   ```bash
   git commit -m "YYYY‑MM‑DD: summary of changes"
   ```
   **Good examples:**
   - `2026‑03‑10: added warrant‑vol‑management topics`
   - `2026‑03‑11: updated pre‑market checklist with ex‑div dates`
   - `2026‑03‑12: fixed delta‑hedge script bug`
   
   **Avoid:** `update`, `fix`, `changes` (too vague).

5. **Push to remote (optional but recommended)**
   ```bash
   git push origin main
   ```
   *Requires a remote repository (GitHub, GitLab, etc.) to be configured.*

## When to Run
- Ideally at the end of each working session (or once per calendar day).
- The cron reminder fires at **18:00 Hong Kong time** as a nudge.

## Troubleshooting
- **Merge conflicts**: Rare in a single‑user workspace, but if they occur, resolve with `git mergetool` or manual editing.
- **Large files**: Avoid committing binary files (PDFs, images) unless necessary; use `business‑documents/` for external papers.
- **Forgot to commit yesterday**: Just commit today with a note like `2026‑03‑11: includes yesterday's uncommitted work`.

## Integration with Knowledge Index
After committing, check if `knowledge/INDEX.md` needs updating:
- New files should be referenced in the index.
- Deleted files should be removed from the index.
- Weekly reviews will handle deeper index maintenance.

---

*This routine is part of the structured‑memory system. Refer to `PROGRAMME.md` for the broader context.*