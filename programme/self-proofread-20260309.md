# Self‑Proofread: Agent Programme Digest
*Date: 2026‑03‑09 · Reviewer: OpenClaw Agent*

## Overview
Compared the proposed digest (`PROGRAMME.md`) against the raw original (`programme/raw/AgentProgramme.txt`). The digest restructures, clarifies, and expands the original while preserving its intent. Below are notes on coverage, ambiguities, and intentional changes.

## Coverage Check ✅

| Section | Original Elements | Digest Coverage | Notes |
|---------|-------------------|-----------------|-------|
| **Introduction** | Two‑version system; iterative refinement; version control; wisdom as hyper‑parameters | Fully covered | Added explicit principles table |
| **Self‑Improving** | Skills upgrade; model optimization; structured memory; routine | Fully covered | |
| **Skills Upgrade** | Grant access to toolkits (skills) | Covered in digest | |
| **Model Optimization** | Choose correct intelligence; multi‑model orchestration; evaluate DeepSeek vs. xAI | Covered | Note: original has incomplete sentence “Before you” – left as TODO |
| **Structured Memory** | Directory tree; root index file; weekly review; Git daily commits; 3 purposes | Fully covered | Added concrete implementation path (`knowledge/INDEX.md`) |
| **Routine** | Weekly review (Programme, Roles, Knowledge) | Covered | |
| **Roles** | Skills vs. roles; execution & project roles; topics/delivery folders; scripts for market summaries | Covered | Fixed typo “delivery.dd” → “delivery” |
| **Trading** | 4 products; execution folder; pre‑market focus; pricing engine; KO management; TV profile; dashboard; evening tasks | Fully covered | Added glossary terms (OI, TV, etc.) |
| **DLC** | Path‑dependent; formula variants; daily support | Covered | |
| **Warrant** | Asian/European; issuer banks | Covered | |
| **CBBC** | Barrier option; residual value | Covered | |
| **Listed Option** | Decentralised; OMM obligations; speed project; stamp exemption | Covered | |
| **Project** | FAFB, Elastic, Stamp Exemption, Warrant Vol Management, Algo Vol Fitter, Street Directed Flow, GED Signal, Alpha | All covered | |
| **Warrant Vol Management** | Cash margin vs. vol following; UsedVol=FitVol+VolMg; pair‑trading formula; margin surface shape | Fully covered with formulas | |
| **Street Directed Flow** | L3 data; broker inheritance; validation; heat conduction; 3‑heatmap dashboard | Covered | |
| **GED Signal** | IV‑RV, skew, z‑scores; backtesting example; learning materials | Covered | |
| **Alpha** | UsedULP formula; lead‑lag PCA; order‑flow spread widening | Covered (noted as incomplete) | |

## Ambiguities & TODOs
1. **Model optimization**: Original ends with “Before you” – likely incomplete. Assumed meaning “before you proceed, evaluate DeepSeek vs. xAI”. **Action**: Ask Operator to clarify.
2. **Alpha project**: Original states “Alpha project is not driven by me, but I’ll fill the details later”. **Action**: Mark as pending future input.
3. **TV profile formula**: Original: `TV(hypothetical spot)*position‑TV(spot)*position`. Digest paraphrased as “theoretical‑value distribution”. **Action**: Verify with Operator if the exact formula should be kept.
4. **Knowledge‑tree root file**: Original mentions “a file where a tree structure inside”. Digest proposes `workspace/knowledge/INDEX.md`. **Action**: Confirm path and format.

## Intentional Changes
1. **Structure**: Added Table of Contents, Glossary, Appendix for implementation notes.
2. **Wording**: Tightened phrasing, fixed typos (“secion” → “section”, “breakeaven” → “breakeven”).
3. **Clarifications**: Expanded acronyms (OI, TV, ULP, etc.) in glossary.
4. **Concreteness**: Suggested folder paths (`Role/topics/`, `Role/delivery/`) and Git workflow.
5. **Separation of concerns**: Moved business‑documents to `business‑documents/`, kept Programme at workspace root as foundational.

## Proposed Location
- **Digested version**: `PROGRAMME.md` (workspace root, alongside `AGENTS.md`, `SOUL.md`).
- **Raw version**: `programme/raw/AgentProgramme.txt` (preserves original wording).
- **Future iterations**: Version‑controlled via Git; weekly review cron to be set up.

## Next Steps
1. **Operator review** of `PROGRAMME.md` for structure, wording, completeness.
2. **Clarify** the above ambiguities.
3. **Sign‑off** → implement folder tree, cron jobs, model evaluation, knowledge‑base commits.

*Proofread complete. Awaiting Operator feedback.*