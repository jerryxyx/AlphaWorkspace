# Overall Architecture Proposal
*For OpenClaw Workspace · Version: Draft 1.0 · Date: 2026‑03‑09*

## Guiding Principles
- **Separation of concerns**: Each domain (roles, trading, projects, knowledge) has its own tree.
- **Consistent pattern**: Where applicable, use `topics/` (knowledge, research, notes) and `delivery/` (scripts, dashboards, outputs) subfolders.
- **Navigability**: A root knowledge‑tree file (`knowledge/INDEX.md`) maps the entire knowledge system with cross‑references.
- **Version control**: Daily Git commits capture incremental changes; weekly reviews audit structure and content.
- **Portability**: The directory tree is self‑contained and can be cloned to new machines, providing a baseline “brain” independent of the underlying LLM.

## Proposed Directory Tree
```
.openclaw/workspace/
├── PROGRAMME.md                     # Core Programme (digested version)
├── AGENTS.md                        # Agent‑workspace guidelines
├── SOUL.md                          # Agent persona
├── USER.md                          # Operator profile
├── TOOLS.md                         # Local tool notes
├── HEARTBEAT.md                     # Periodic‑check tasks
├── IDENTITY.md                      # Agent identity
├── programme/                       # Programme evolution
│   ├── raw/AgentProgramme.txt       # Original Operator draft
│   ├── digested/                    # Versioned digested copies (optional)
│   └── reviews/                     # Proofreads, review notes
├── roles/                           # Capability profiles
│   ├── trading‑execution/
│   │   ├── topics/                  # Market summaries, decision trees, workflows
│   │   └── delivery/                # Scripts, dashboards, attention‑optimizer logs
│   └── trading‑project/
│       ├── topics/                  # Quantitative research, models, math
│       └── delivery/                # Code, backtests, visualizations
├── knowledge/                       # Structured memory system
│   ├── INDEX.md                     # Root knowledge tree (maps all domains)
│   ├── trading/                     # Product specs, market mechanics, risk concepts
│   ├── quantitative/                # Models, formulas, derivations
│   └── operational/                 # Tools, processes, Git workflows
├── trading/                         # Trading‑domain content
│   ├── products/                    # Per‑product knowledge & tools
│   │   ├── warrants/
│   │   │   ├── topics/              # Asian/European specs, issuer details
│   │   │   └── delivery/            # Pricing scripts, margin calculators
│   │   ├── cbbcs/
│   │   │   ├── topics/              # Barrier‑option mechanics, KO/residual‑value formulas
│   │   │   └── delivery/            # KO‑hedge scripts, TV‑profile monitors
│   │   ├── listed‑options/
│   │   │   ├── topics/              # OMM obligations, American/European differences
│   │   │   └── delivery/            # Speed‑optimization scripts, stamp‑exemption tools
│   │   └── dlc/
│   │       ├── topics/              # Path‑dependent formulas, term‑sheet variants
│   │       └── delivery/            # Intrinsic‑value replicators, daily‑check scripts
│   └── execution/                   # Cross‑product execution support
│       ├── topics/                  # Pre‑market checklist, intraday alerts, KO handling
│       └── delivery/                # Dashboard, P&L/risk monitors, slippage trackers
├── project/                         # Project‑domain content
│   ├── warrant‑vol‑management/
│   │   ├── topics/                  # Cash‑margin math, vol‑surface research
│   │   └── delivery/                # MC simulations, margin‑surface generator
│   ├── algo‑vol‑fitter/
│   │   ├── topics/                  # Real‑time vol‑fitting algorithms, data pipelines
│   │   └── delivery/                # Fitter implementation, latency benchmarks
│   ├── street‑directed‑flow/
│   │   ├── topics/                  # L3 order data, broker inheritance, flow prediction
│   │   └── delivery/                # Flow estimator, heat‑map dashboards
│   ├── ged‑signal/
│   │   ├── topics/                  # IV‑RV, skew, z‑score calculations, backtesting
│   │   └── delivery/                # Signal generator, portfolio‑simulation tools
│   ├── stamp‑exemption/
│   │   ├── topics/                  # HKEX rules, option‑flow simulation, stamp‑duty logic
│   │   └── delivery/                # Trade‑qualification scripts, exemption tracker
│   ├── fafb/
│   │   ├── topics/                  # FA/FB parameters, event‑driven spread widening
│   │   └── delivery/                # Parameter‑tuning scripts, convergence monitors
│   ├── elastic/
│   │   ├── topics/                  # Toxic‑flow detection, broker‑ID patterns
│   │   └── delivery/                # Liquidity‑drop algorithms, spread‑adjustment logic
│   └── alpha/
│       ├── topics/                  # Lead‑lag PCA, order‑flow spread models (placeholder)
│       └── delivery/                # (placeholder for future deliverables)
├── business‑documents/              # External papers, reports, competitor analysis
├── memory/                          # Temporal logs
│   ├── daily/2026‑03‑09.md          # Raw daily notes
│   ├── weekly/                      # Weekly summaries
│   └── long‑term/                   # Curated memories (distilled from daily)
├── skills/                          # OpenClaw skills (existing)
└── .git/                            # Version control
```

## How It Works
### 1. **Knowledge System (`knowledge/`)**
- **`INDEX.md`** is the central map. It contains a hierarchical outline linking to key files across the workspace (e.g., `[Warrant Vol Management](../project/warrant‑vol‑management/topics/cash‑margin.md)`).
- Weekly reviews update `INDEX.md` to reflect additions/removals.
- Subfolders (`trading/`, `quantitative/`, `operational/`) store deeper, domain‑specific notes that are referenced by the index.

### 2. **Roles (`roles/`)**
- Each role is a capability profile with its own `topics/` (what the role needs to know) and `delivery/` (what the role produces).
- **Example**: `roles/trading‑execution/topics/pre‑market‑checklist.md` lists ex‑div dates, spot moves, news; `delivery/` contains scripts that generate morning summaries.

### 3. **Trading (`trading/`)**
- Mirrors the desk’s product‑based organization.
- `products/` holds product‑specific knowledge/tools; `execution/` houses cross‑product workflows and dashboards.
- Consistent `topics/`‑`delivery/` pattern allows uniform navigation.

### 4. **Projects (`project/`)**
- Each project follows the same `topics/` (research, math) and `delivery/` (code, simulations, visualizations) structure.
- Facilitates parallel work and clear separation of knowledge from deliverables.

### 5. **Memory (`memory/`)**
- **Daily logs** capture raw events, decisions, lessons.
- **Weekly summaries** distill patterns.
- **Long‑term memory** stores curated insights (eventually merged into `MEMORY.md` for main‑session use).

### 6. **Programme (`programme/`)**
- Houses the raw original, digested versions, and review notes.
- Ensures the Programme itself is version‑controlled and iterable.

## Naming Conventions
- **Folder names**: Singular, lowercase, hyphen‑separated (e.g., `trading‑execution`, `warrant‑vol‑management`).
- **Topics vs. delivery**: 
  - `topics/` – knowledge, research, notes (inputs).
  - `delivery/` – scripts, dashboards, outputs (deliverables).
- **Programme**: British‑English spelling retained to match the core document (`Agent Programme`).
- **Consistency**: The `topics/`‑`delivery/` pattern is applied uniformly across all projects and products.

## Git Strategy
- **Daily commits**: At the end of each session, commit changes with a descriptive message (e.g., `git commit -am “2026‑03‑09: added warrant‑vol‑management topics”`).
- **Weekly reviews**: Every Sunday (or ad‑hoc), run a diff against the previous week, update `knowledge/INDEX.md`, and tag the commit (e.g., `week‑2026‑03‑13`).
- **Remote backup**: Push to a private repository (GitHub, GitLab, etc.) for off‑machine backup and portability.

## Benefits
- **Clarity**: Anyone (Operator or Agent) can navigate the workspace and understand where knowledge lives.
- **Traceability**: Decisions are linked to specific files; Git history shows evolution.
- **Scalability**: New roles, products, or projects slot in without disrupting existing structure.
- **Resilience**: The knowledge tree survives LLM model changes; cloning the workspace to a new machine restores the “brain”.

## Next Steps (Upon Operator Sign‑off)
1. Create the directory tree (script provided).
2. Populate `knowledge/INDEX.md` with initial skeleton.
3. Migrate any existing notes to the appropriate locations.
4. Set up weekly review cron job.
5. Begin daily Git‑commit habit.

---

*This architecture is proposed as a foundation for the Agent Programme. Feedback and adjustments welcome before implementation.*