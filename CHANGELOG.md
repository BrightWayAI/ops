# Changelog

All notable changes to ops (formerly core-ops) are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versions match `plugin.json`.

## [0.18.0] — daily-nudges schedule; two verify fixes (2026-11-16)

### Added
- Schedule library row `daily-nudges`: weekdays 06:30, growth's `/nudges`, `cloud`, optional. `/register-schedules` offers it when growth is installed and registers it only on a yes. `/status` shows its last success and staged count; a stale nudges run is a warning and does not make the scheduled loop unhealthy.

### Fixed
- A cloud registration recorded as `unverified-until-first-receipt` now has `last_verified_at: null`. It was stamped as verified at registration, before any run had proven it could reach the config root.
- `--verify` now also checks a library row that has a live task but no record. The `no-folder-binding` repair instruction told the user to fix the task and re-run `--verify`, but `--verify` only looked at rows that already had a record, so a repaired task was never picked up.

## [0.17.1] — chief-of-staff tool allowlist (2026-11-16)

### Changed
- `chief-of-staff` now has a tool allowlist: `Read, Grep, Glob`. It could previously reach every tool in the parent session; it is a route planner and needs none of them.

## [0.17.0] — Receipts and registrations record the actor (2026-11-16)

### Changed
- Run-receipt schema 1.1.0 (`/register-schedules` Step 5): required `actor_id` and `actor_source`; `outcome` is `succeeded | partial | skipped | failed`. Readers accept the 1.0.0 shapes too.
- `/register-schedules` puts a sentence naming the actor in every registered prompt, stores `registered_by` in the registration record, and stops with a pointer to `/setup-identity` when no identity exists. Earlier registrations keep working and are offered a prompt update.
- `/status` shows who the last run acted for, treats a receipt with no actor as "not recorded", and warns on `actor_id: "unresolved"`. It also accepts `outcome: "succeeded"`, which cortex has been writing and `/status` did not previously recognize.
- The agent-run log gains `actor_id`.

### Added
- Eval `receipt-records-actor`.

## [0.16.0] — Route plans use the three risk tiers (2026-11-16)

### Changed
- `/cos` route plans use `risk_tier: low | medium | high | never` (was `always | ask_first | never`), matching autonomy policy 2.0.0 in cortex 4.34.0. Execution rule 5: low runs, medium is shown once as a batch and written after the user accepts, high is previewed and approved immediately before each item. The plan's tier is an estimate; a higher tier applies if the workflow does more. With a 1.0.0-shape policy there is no medium tier and medium is handled as high.
- `chief-of-staff` classifies by the highest tier of anything the workflow does, and `high` when unsure.

### Added
- Eval `cos-risk-tier-execution`.

## [0.15.1] — Routing evals carry a plugin catalog (2026-11-16)

### Changed
- The seven routing evals now state the installed sibling-plugin catalog in `append_system_prompt` and end with the route plan. An eval run loads only this plugin, so the router previously returned `unsupported` in every case. `evals/README.md` says how to run the suite. No command behavior changed.

## [0.15.0] — Cloud-capable schedules (2026-11-16)

### Added
- **`Runs on` column in the schedule library** (`cloud` | `local-device`). `references/schedules.template.md` no longer says every row must register with `requires_local_device=true`; that contradicted the cloud-first sync in cortex 4.29, under which `/listen` runs as a cloud routine with no device attached. `nightly-listen` now defaults to `cloud`; the two optional rows stay `local-device`.
- `/register-schedules` registers a `cloud` row with `requires_local_device=false`, no folders and the two sync repositories attached, and does not fail it for an empty folder list. A cloud row whose attached repositories the scheduler cannot show is recorded as `binding: "unverified-until-first-receipt"`. A workflow with no cloud contract is reported `unavailable: no-cloud-contract`.
- `/register-schedules` refuses to keep the same schedule registered in both modes without asking which to keep.
- Eval `register-schedules-cloud-row`.

### Changed
- Registration-state schema `1.0.0` → `1.1.0`: adds `runs_on` and `binding`. A `1.0.0` record is read as `local-device` / `verified` and rewritten on its next update.
- `/status` SCHEDULED LOOP checks a cloud row for "enabled, no device requirement, receipt present in the local copy" instead of folder binding, and reports `stale: local-copy-not-synced` when only the local copy is behind.
- Eval `register-schedules-no-folder-binding` states that its row is `local-device`.

### Compatibility
- A definitions file without the column behaves exactly as before: every row is `local-device`, its fingerprint is unchanged, and existing registrations stay `current`.

## [0.14.2] — Agent-log examples use current names (2026-11-16)

### Fixed
- `references/agent-log-schema.md` and `commands/log-agent-run.md` examples no longer name retired agents and commands (`contact-researcher`, `bizdev-outreach`, `/lead-brief`, `/weekly-outreach`, `/ai-roundup`). They now use `relationships-director`, `/relationships`, `/pre-call-brief` and `/roundup`. The schema and log path are unchanged.

## [0.14.1] — Cloud config-root portability (2026-10-30)

### Fixed
- Align OpenAI root resolution with Cortex, including materialized cloud roots and unreachable-root checks.
- Specify cloud bootstrap/sync, private-repo boundaries, MCP-only degradation, and per-schedule verification.

## [0.14.0] — Unreachable config root is detected and explained (2026-10-30)

Unreachable config root is now detected and explained at every entry point (cloud sessions especially).

### Changed
- `/status` Step 0 runs cortex's `root-status` first. If the root is unreachable it prints a **BROKEN** block with one sentence and the exact fix, still lists connectors, and marks filesystem sections "blocked: config root not attached" instead of "unknown". Scheduled Loop also reads `~/.cortex/pending-receipts/` for `config_root_unreachable` receipts.
- `/diagnose` gains the same Step 0.
- `/setup-core` recommends `~/cortex-root` (and warns off Documents/Desktop/Downloads/iCloud) instead of suggesting `~/Documents/Claude/`; schema docs no longer point backups at `~/Documents/Claude/`.

## [0.13.0] — Schedule folder-binding enforcement (2026-09-18)

### Fixed
- `nightly-listen` (and every other schedule in the library) could be registered without device/folder binding and would report scheduler "success" every night while never actually reaching `<config-root>`. `/register-schedules` now requires `requires_local_device=true` and `folders=[<config-root>]` on every registration and verifies the binding via `list_triggers`/`derived_state` immediately after `create_trigger` — a row that fails verification is reported `failed: no-folder-binding` and no registration-state record is written for it.

### Added
- `/register-schedules --verify` — read-only mode that re-checks an already-registered host task's folder binding and bumps `last_verified_at`, without creating/updating/deleting anything.
- Definition fingerprint now includes `requires_local_device` + `folders`, so pre-existing registrations made before this requirement (including the live `nightly-listen` task) classify as `changed` and get re-registered with proper binding on the next `/register-schedules` run.
- Registered prompts must now include an explicit instruction to fail loudly (`error_code: config_root_unreachable`, non-zero exit, no receipt claiming success) when `<config-root>` is unreachable at run time.
- `/status`'s SCHEDULED LOOP section no longer trusts the scheduler's own success flag — it requires a recent (`<26h`) succeeded receipt AND a verified live folder binding (via `--verify`, read-only) before reporting healthy.
- `README.md` and cortex's `/start-nucleus` now state the device/folder-binding requirement for `nightly-listen` up front.

## [0.12.1] — OpenAI SOW routing hardening (2026-09-16)

### Fixed
- `/diagnose` now verifies Ops as a routing and stack-operations plugin instead of incorrectly claiming it reads CRM pipeline stages after that responsibility moved to Growth Engine.
- Updated the canonical repository URL from the retired `core-ops` name to `ops`; legacy GitHub redirects remain compatible.
- `/status` and `/diagnose` distinguish complete SOW templates from pre-0.7.1 files that lack approved boilerplate instead of treating file existence as sufficient.

## [0.11.1] — OpenAI host adapter (2026-09-14)

### Added
- Native Codex/ChatGPT plugin manifest, durable `AGENTS.md` entrypoint, and an explicit OpenAI capability/degradation contract.
- GPT-discoverable skill aliases for canonical command workflows and read-only Codex role bindings where this plugin ships agents.
- Shared config-root resolution compatible with Cortex and Claude; all GPT tests use repository fixtures or temporary directories only.

## [0.12.0] — Eval suite: chief-of-staff routing cases (2026-09-15)

### Added
- Six new `claude plugin eval` cases in `evals/` extending the existing `chief-of-staff-natural-language` case: `catch-me-up-natural-language`, `follow-up-routing-natural-language` (routes to `growth`), `draft-checkin-routing-natural-language` (routes to `comms`), `ask-client-success-routing-natural-language` (role-addressed, routes to `clients`), `bill-routing-natural-language` (routes to `admin`), and `team-misaligned-routing-natural-language` (routes to `alignment`). All `llm`-graded, checking `/cos` produces a structured route plan and delegates rather than executing the target workflow itself.

## [0.11.0] — Phase 3 consistency fixes (2026-09-15)

### Changed
- `references/schedules.template.md` reduced to exactly three registrable schedules: `nightly-listen` (required), `weekly-end-week` (optional), `weekly-roundup` (optional, relevant only when `research` is installed). Added a Required/Optional column to the schedule table.
- `commands/register-schedules.md` Step 0 now registers only `nightly-listen` by default, mentions `weekly-end-week`/`weekly-roundup` as available-but-not-auto-registered, and tells the user up front that the host must be awake at run time and that first-run tool-use approvals should be granted with "always allow."

## [0.10.0] — `/setup-voice` ownership moves to Comms Desk (2026-09-15)

### Changed
- `README.md`, `commands/status.md`, `commands/diagnose.md` updated to attribute `/setup-voice` to the `comms` plugin (Comms Desk) instead of `cortex` — the interview moved there, while `<config-root>/memory/me/voice.md` remains a Cortex-owned canonical file.

## [0.8.0] — pipeline agents move to growth (2026-09-15)

### Changed
- `pipeline-analyst` and `pipeline-forecast` subagents (and their Codex mirrors) moved to the `growth` plugin. `chief-of-staff` (`/cos`) now delegates to `growth:pipeline-analyst` / `growth:pipeline-forecast` when growth is installed, and reports "Growth Engine not installed; pipeline analysis skipped" otherwise. Ops no longer reads the CRM directly.
- Updated README, SECURITY.md, `/diagnose`, `/setup-core`, `skills/setup/SKILL.md`, and reference templates to reflect the new ownership.

## [0.9.0] — `/dashboard` moved to briefing (2026-09-15)

### Removed
- `/dashboard` (rich visual Cowork-artifact stack surface), its skill, and `references/nucleus-dashboard-template.html` moved to the `briefing` plugin (Today's Brief), per the "Today's Brief is every what's-going-on surface at any cadence" container rule. `ops` retains `/status` (terse text snapshot) and `/diagnose` (troubleshooting) — these explicitly did NOT move.

### Changed
- `/nucleus-dashboard` (the existing deprecated alias) now routes to `briefing:dashboard` instead of an in-plugin `/dashboard`, with a degraded-mode skip + `/status` suggestion if `briefing` isn't installed.
- `/status` and its skill updated to point at briefing's `/dashboard` for the richer visual surface.

## [0.7.0] — Renamed to ops (2026-09-15)

### Changed
- Renamed from `core-ops` to `ops` (display name: Chief of Staff) as part of the 2026-09-15 Nucleus plugin rename. Old plugin ID/repo name redirects; see marketplace catalog.
- `/nucleus-status` renamed to `/status`; `/nucleus-dashboard` renamed to `/dashboard`. Old command names remain as deprecated one-line aliases.

## [0.6.4] — routing and schedule-state hardening (2026-09-15)

### Changed
- Split chief-of-staff route planning from parent-owned execution with a structured route-plan contract and narrower triggers.
- Moved schedule definitions, per-host IDs, and metadata-only run receipts into separate user-owned config-root paths.
- Updated status, diagnostics, dashboard, and connector ownership for the nine-plugin catalog.

## [0.6.3] — Codex adapter synchronization (2026-09-15)

### Added
- Read-only Codex binding and OpenAI host preamble for the `chief-of-staff` `/cos` entrypoint.

### Fixed
- Updated Codex metadata and degraded behavior after deliverable QA moved to `delivery`.

## [0.6.2] — claude plugin eval suite (2026-09-15)

Nucleus Operating Model Refactor Phase 4 step 4.2.

### Added
- `evals/chief-of-staff-natural-language/` — eval case testing the chief-of-staff agent's open-ended natural-language routing, with an `llm` grader
  checking the response acts on the natural-language request directly rather
  than asking the user to type the explicit command. Run with
  `claude plugin eval . --case chief-of-staff-natural-language`; `--ablation with-without`
  (the default when the plugin resolves) reports the delta between installed
  and not — a delta near zero means the skill's description isn't matching
  natural phrasing and needs work.
- `.gitignore` — excludes `evals/results/` (per-run output, not checked in).

## [0.6.1] — Skill auto-invocation audit (2026-09-15)

Nucleus Operating Model Refactor Phase 3 step 3.7. Ritual and side-effecting
skills marked `disable-model-invocation: true` so they only run on explicit
invocation, not loose natural-language matching — the model can still be
asked to run them by name. Read-mostly, low-stakes, or high-frequency
conversational skills are left auto-invocable. Marketplace-wide this brings
model-invocable skills from ~81 to 27, under the ≤30 target audited with
`/skill-doctor`.

### Changed
- Marked `disable-model-invocation: true` on: `log-agent-run`, `register-schedules`, `setup`, `setup-core`, `test-connectors`.

## [0.6.0] — chief-of-staff agent + /cos, nucleus-router retired (2026-09-15)

Nucleus Operating Model Refactor Phase 3 step 3.1. Adds the natural-language
front door that replaces the standalone `nucleus-router` plugin.

### Added
- `agents/chief-of-staff.md` — job-description-style agent (purpose, goals,
  success/failure criteria, escalation rules, tools). Loads
  `<config-root>/memory/hot.md` + `index.md`, reads the autonomy policy in
  `memory/CLAUDE.md`, and routes natural-language or role-addressed requests
  to the matching installed plugin command. Narrates read-only/drafting work;
  confirms before ASK FIRST/NEVER-tier actions.
- `/cos` command — explicit invocation of the agent.
- `skills/cos/SKILL.md` — always-loaded routing skill, thin wrapper around
  the agent (no inline intent tables — routing logic lives in the job
  description, per the refactor's "agents are job descriptions, not
  procedures" principle).

### Removed
- Retired the `nucleus-router` plugin entirely (archived on GitHub with a
  redirect README pointing at `/cos` in this plugin; local clone removed).
  Cross-references in `relationships` skill docs and cortex's
  `references/autonomy.md` updated to point at the chief-of-staff agent.

## [0.5.0] — /review-deliverable moved to delivery (2026-09-15)

Nucleus Operating Model Refactor Phase 3 step 3.3. `project-setup` renamed to
`delivery` and absorbed `client-status` + this plugin's `/review-deliverable`.

### Removed
- `commands/review-deliverable.md`, `skills/review-deliverable/SKILL.md` —
  moved to the `delivery` plugin. Brand/CRM config (`core-ops.user-context.md`)
  stays owned by this plugin; `delivery` reads it cross-plugin, same pattern
  as `relationships` reading CRM config from here.

## [0.4.4] — writing-style renamed to voice (2026-09-15)

### Changed
- `commands/nucleus-status.md` — plugin-name and config-file references updated
  from `writing-style` to `voice` (Nucleus Operating Model Refactor Phase 3
  step 3.4).

## [0.4.3] — Identity/voice moved to memory/me/ (2026-09-15)

### Changed
- Path references updated from `<config-root>/identity.md` / `<config-root>/voice.md` to `<config-root>/memory/me/identity.md` / `<config-root>/memory/me/voice.md`, per the Nucleus Operating Model Refactor Phase 2 scopes restructure (identity/voice are personal, not org-shared facts). No behavior change beyond the path.

## [0.4.2] — Diagnose reports memory cap violations (2026-09-15)

### Added
- `/diagnose` Step 1E — reports cortex's `check-caps` output as a health line
  (`Memory caps: clean` or `Memory caps: N FAIL, M WARN`). A FAIL is treated
  as a ✗, since it means `/recall`'s default load boundary is broken for at
  least one node. Part of the Nucleus Operating Model Refactor, Phase 2 step
  2.3.

## [0.4.1] — Instantiate schedule library (2026-09-15)

### Added
- `references/schedules.md`, instantiated from the template for the first time (zero
  schedules had ever been registered). Populates `nightly-listen` only, with a
  run-window guard and the exact registration prompt for `/register-schedules` to hand
  to Cowork. Part of the Nucleus Operating Model Refactor, Phase 1 step 1.4.

## [0.4.0] — Live connector certification (2026-09-15)

### Added
- `/test-connectors` and its matching skill. The workflow performs real, bounded,
  read-only calls against authorized calendar, mail, CRM, Slack, Drive, contact
  enrichment, and transcript connectors.
- Metadata-only JSON evidence compatible with Nucleus's deterministic connector-report
  validator and coordinated release gate.
- Explicit cross-host certification: Claude and ChatGPT runs remain separate because
  connector authorization and tool schemas are host-specific.

## [0.3.3] — OpenAI host adapter (2026-09-14)

### Added
- Native Codex/ChatGPT plugin manifest, durable `AGENTS.md` entrypoint, and an explicit OpenAI capability/degradation contract.
- GPT-discoverable skill aliases for canonical command workflows and read-only Codex role bindings where this plugin ships agents.
- Shared config-root resolution compatible with Cortex and Claude; all GPT tests use repository fixtures or temporary directories only.

## [0.3.2] — /diagnose memory-as-git health line (2026-06-08)

### Added
- `/diagnose` Step 1D — memory-as-git health check (closes the last build-plan item of the cortex memory-as-git proposal). Reports enabled? / last-commit / clean-tree / remote status as one informational line in the Step 5 checklist. Coordinated with cortex v4.13.0.

## [0.3.1] — Schedule library: /listen + /research-gaps (2026-05-16)

### Added
- `nightly-listen` schedule row in `references/schedules.template.md` — registers `/listen` (cortex v4.7+) at 11pm daily for unattended overnight ingest. Recommended for users running cortex with `/setup-sources` configured.
- `weekly-research-gaps` schedule row — registers `/research-gaps` (cortex v4.5+) at 9am Saturday for weekly autonomous gap-fill scans.

### Why
cortex v4.7 shipped `/listen` for nightly autonomous ingest. Without a registered cron, the pipeline never runs. This patch adds the schedule entry so `/register-schedules` automatically wires it. Same for `/research-gaps`'s recommended weekly cadence.

### Migration
Existing users on v0.3.0 should re-run `/register-schedules` after updating to v0.3.1. The new rows are registered as new entries; pre-existing schedules remain (idempotent — register-schedules uses the `last_registered_id` annotation to skip duplicates).

## [0.3.0] — Nucleus visibility layer (2026-05-12)

### Added
- **`/nucleus-status`** — at-a-glance text snapshot of the Nucleus stack. Installed plugins, setup state (configured/template/missing), connector availability, recent activity, memory health, anything broken. Terse output (~30-40 lines), fits in chat, scannable in 10 seconds. Read-only. Zero model calls.
- **`/nucleus-dashboard`** v1 — rich visual dashboard as a Cowork HTML artifact titled "Nucleus Dashboard." Six section cards: Stack overview, This week (activity histogram + top skills + rusty skills), Cortex memory health (decay state distribution + person pages + triage log), Outreach pipeline (lead-engine), Time + invoicing (time-tracking), Impact loop (v1 placeholder; v1.1 ships content). Re-renders on demand via `/nucleus-dashboard`. Markdown snapshot fallback at `<config-root>/nucleus-dashboard.md` in Claude Code. Zero model calls.
- **`references/nucleus-dashboard-template.html`** — bundled HTML template with inline SVG charts. No external libraries.
- **Both commands gracefully degrade.** Missing connectors, missing memory, missing telemetry — each section renders an honest placeholder rather than failing the whole render.

### Why this matters
With the marketplace at 13 plugins and the second-brain layer in active use, users (starting with the solo founder, scaling to teams) need a way to see what's installed, what's configured, what's running, and what their system is producing — without grepping the filesystem manually. `/nucleus-status` is the quick check; `/nucleus-dashboard` is the live surface. Both sit alongside `/diagnose` (troubleshooting) in core-ops as the visibility cluster.

### Roadmap
- v1.1 adds the Impact loop section content (drafted→sent ratios across drafting plugins, mining proposal accept rate, P0 completion rate). Deferred from v1 because the metrics need a week of telemetry to populate sensibly.

## [0.2.3] — Platform-agnostic Step 0 (2026-05-12)

### Changed
- **Setup command Step 0 now platform-agnostic.** Every `request_cowork_directory(...)` call is conditional: "In Cowork, call `request_cowork_directory(...)`. In Claude Code (or any environment with direct filesystem access), no mount is needed." Same plugin source works in both runtimes.

### Why this matters
Phase 0 of SECOND-BRAIN-V2-SPEC. Removes the implicit Cowork-only assumption so Claude Code users do not hit unsupported tool calls during setup.

## [0.2.0] — Config-root refactor + previously in-flight features

### Changed (config-root refactor)
- **Plugin config moved to a user-chosen folder.** All reads and writes of `references/user-context.md` (which was inside the plugin's source folder — read-only under Cowork's mount) now go to `<config-root>/plugins/core-ops.user-context.md`, where `<config-root>` is the folder the user chooses on first plugin setup (recorded at `~/Documents/.claude-plugin-config-root`). Without this, the plugin's setup writes failed silently under Cowork.
- **`/setup-core` Step 0 now bootstraps the config root.** Reads `~/Documents/.claude-plugin-config-root` first. If missing, prompts the user for the config root, persists their choice, mounts it via `request_cowork_directory`, and offers to migrate existing `~/Documents/Claude/identity.md` / `voice.md` and any pre-staged `~/Documents/Claude/plugin-configs/*.user-context.md` files.
- **All operating skills, commands, and agents** (`/review-deliverable`, `/diagnose`, `/log-agent-run`, `/agent-metrics`, `/register-schedules`, `pipeline-analyst`, `pipeline-forecast`) now read from `<config-root>/plugins/core-ops.user-context.md` instead of the old plugin-relative path.
- **User-facing prompts and skill descriptions debranded.** "BrightWayAI marketplace plugins" → "marketplace plugins"; "BrightWayAI plugin" → "marketplace plugin." The marketplace is fork-friendly — any user can install and run.

### Added (previously in-flight, now formally released)
- `pipeline-forecast` subagent — forward-looking revenue projection. Companion to `pipeline-analyst`. Uses stage probabilities × deal values × historical close rates to project a future window. Returns scenarios (best / expected / worst / stretch), needle-mover deals, gap-to-target analysis, structural risks. Useful for monthly planning, runway analysis, board reporting.
- `/diagnose` — ecosystem health check. Audits shared config files (`identity.md`, `voice.md`, cortex memory), plugin setup state, subagent availability, connector wiring. Surfaces specific fix instructions ranked by impact.
- `/log-agent-run` and `/agent-metrics` — lightweight telemetry. Append-only meta-log capturing agent / parent skill / confidence / user action. Privacy-respecting (no message content, no sensitive data). `/agent-metrics` produces read-only digests for trend analysis.
- `/register-schedules` and `references/schedules.template.md` — versioned schedule library. Bulk-register standing schedules with Cowork's scheduled-tasks system. Useful for new-machine setup and reproducibility across machines.
- `references/agent-log-schema.md` — JSONL schema documentation for the agent-run log.

## [0.1.0] — Initial release

### Added
- Plugin renamed from `brightway-core` to `core-ops` for generic reuse (BrightWay-specific naming removed from plugin name).
- `pipeline-analyst` subagent — point-in-time CRM ranking. Scores and ranks pipeline by recency × signal strength × stage. Used by `weekly-outreach`, `plan-tomorrow`, any pipeline-review workflow.
- `/review-deliverable` slash command — structured QA pass on a client deliverable (deck, doc, spreadsheet, one-pager) against the user's brand guide and the original brief. Returns location-tagged findings ranked by severity, plus a ship/no-ship verdict.
- `/setup-core` interview — captures CRM context, brand context, owner info. Writes to `references/user-context.md` (gitignored).
- Generic by design — works with any CRM and any brand once configured.
