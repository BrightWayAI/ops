# ops

A generic business-ops toolkit for Claude (Cowork + Claude Code).

The shared-utility plugin that other plugins in the [BrightWayAI marketplace](https://github.com/BrightWayAI/nucleus) lean on. Hosts the natural-language front door (`/cos`) and the cross-cutting infrastructure commands (`/diagnose`, telemetry, schedule library). Configurable per user via `/setup-core` — works with any CRM and any brand once configured. As of 2026-09-15, the `pipeline-analyst` and `pipeline-forecast` CRM-intelligence subagents live in the `growth` plugin — `/cos` delegates to `growth:pipeline-analyst` / `growth:pipeline-forecast` when growth is installed, and shows "Growth not installed; pipeline analysis skipped" otherwise.

## What's inside

### Agents (1)

- **`chief-of-staff`** — the read-only route planner behind `/cos`. Given a request and the installed workflow catalog, it returns one route plan: a single workflow, or up to four parallel read-and-draft workers for a request that spans several areas, plus any later steps that write or send, each with its risk tier. It routes by what the request is about and never executes, writes, or sends; the parent validates the plan and runs it under the autonomy policy. Its tools are limited to reading and searching files. (The agent keeps its original name; it is a planner, not a persona.)

### Slash commands (8, plus 2 deprecated aliases)

- **`/cos`** — the natural-language front door. Say what you need and it routes to the installed workflow that does it; also fires implicitly on plain conversation via `skills/cos/SKILL.md` wherever the host supports always-loaded skill routing.
- **`/setup-core`** — interview that captures CRM context, brand context, and owner info. Writes to `<config-root>/plugins/ops.user-context.md`.
- **`/status`** — at-a-glance snapshot of your Nucleus stack in chat: installed plugins, setup state, connector availability, last runs (including the nightly run), anything broken. Readable in ten seconds. For a visual version use briefing's `/dashboard`.
- **`/diagnose`** — ecosystem health check. Audits shared config files (`identity.md`, `voice.md`, cortex memory), plugin setup state, subagent availability, connector wiring. Produces a green/red checklist with specific fix instructions.
- **`/test-connectors`** — performs bounded, read-only calls against real authorized connectors and returns a sanitized release-certification report. User assertions and mocked payloads cannot pass.
- **`/log-agent-run`** — record what you did with a sub-agent's output in `<config-root>/plugins/ops/agent-runs/``notes.jsonl`. Sub-agent runs themselves are logged automatically by the plugin's hooks. Captures agent / parent skill / confidence / user action — never message content.
- **`/agent-metrics`** — read-only digest of the agent log. Surfaces top performers, slipping agents, high-abandonment paths, confidence trends.
- **`/register-schedules`** — reconcile user-owned definitions from `<config-root>/plugins/ops/schedules.md` with the active host scheduler. Useful for new-machine setup or after scheduler reinstall. Each row declares where it runs. A `cloud` row (the default for `nightly-listen`) runs with no computer attached and reaches the config root by bootstrapping the two sync repositories at the start of the run. A `local-device` row binds to the specific Mac the registering conversation is linked to — the Claude desktop app must be running and that Mac must be awake and online at fire time, or the run is skipped until the next window. A definitions file without a `Runs on` column is treated as all `local-device`. `--verify` re-checks an already-registered task's binding without re-registering it.
- **`/nucleus-status`**, **`/nucleus-dashboard`** — deprecated aliases for `/status` and briefing's `/dashboard`, kept so old invocations and schedules keep working.

### Hooks

`hooks/log_agent_run.py` records every sub-agent run automatically (agent, parent skill, timing — never message content). `/log-agent-run` adds your judgment on top.

## Install

Recommended: install via the [BrightWayAI marketplace](https://github.com/BrightWayAI/nucleus).

```
/plugin marketplace add BrightWayAI/nucleus
/plugin install ops@nucleus
```

## First-time setup

The plugin reads two shared user-level config files (created by cortex's `/setup-identity` and Comms's `/setup-voice`) before its own setup, so identity and voice questions don't get re-asked here.

Then run `/setup-core`. The interview captures:

- **CRM context** — which CRM you use, which pipeline stages matter, what "good" looks like for prioritization, optional historical close rates for forecasting.
- **Brand context** — brand colors, typography, tone-of-voice rules, optional path to your brand guide.
- **Owner info** — anything not already in shared identity.

Saved to `<config-root>/plugins/ops.user-context.md`.

You can re-run `/setup-core` anytime to update.

## Companion plugins

This plugin is a hub — many other plugins delegate to `/cos` and `/diagnose`:

- **growth** owns `pipeline-analyst` / `pipeline-forecast`; briefing calls `growth:pipeline-analyst` for daily prioritization.
- **Admin + Clients** integrate with `growth:pipeline-analyst` to surface revenue-vs-time and engagement-vs-pipeline views.
- All plugins benefit from `/diagnose` to verify setup state.
- `/register-schedules` orchestrates standing schedules across the whole marketplace.

## What's inside (file tree)

```
.claude-plugin/plugin.json     Plugin manifest
agents/
  chief-of-staff.md            Agent: read-only route planner behind /cos
commands/
  cos.md                       Natural-language front door
  status.md                    At-a-glance stack snapshot
  setup-core.md                Interview and config writer
  diagnose.md                  Ecosystem health check
  test-connectors.md           Live, read-only connector certification
  log-agent-run.md             Telemetry: record what you did with an agent's output
  agent-metrics.md             Telemetry: read-only log digest
  register-schedules.md        Register schedules from your definitions file
  nucleus-status.md            Deprecated alias → /status
  nucleus-dashboard.md         Deprecated alias → briefing's /dashboard
hooks/
  hooks.json                   Registers the sub-agent run logger
  log_agent_run.py             Logs each sub-agent run automatically
skills/
  <one per command>/SKILL.md   Fires the matching command from plain language
  setup/SKILL.md               Auto-fires on setup phrases
references/
  user-context.template.md     Structure (committed)
  user-context.md              Your config (gitignored, created by setup)
  agent-log-schema.md          JSONL schema for the agent-run log
  schedules.template.md        Immutable starter schedule library
  schedules.md                 Immutable schema and workflow reference
```

## Dependencies

- **CRM connector** (HubSpot / Salesforce / Pipedrive / Attio / etc.) — optional; used by `/test-connectors` and by growth's pipeline agents when `/cos` routes to them.
- **A host scheduler** (Cowork's scheduled tasks, or cloud routines) — required for `/register-schedules` to register schedules.

<!-- OPENAI-SUPPORT:START -->
## ChatGPT and Codex

Ops ships as a native OpenAI plugin as well as a Claude plugin. In
ChatGPT desktop Local Work, enable **Ops** and ask naturally or mention
`@Ops`. In Codex, use natural language or the namespaced skills exposed
by the plugin. Claude slash-command names in this README remain workflow aliases.

All hosts resolve the same `<config-root>` used by Cortex, so Claude, ChatGPT desktop,
and Codex can share identity, voice, memory, and per-plugin settings without copying
them. The installed plugin directory is read-only at runtime. See
[`references/openai-portability.md`](references/openai-portability.md) for capability
mapping, connector checks, permissions, and honest degraded behavior.

Import the full catalog from
[`BrightWayAI/nucleus`](https://github.com/BrightWayAI/nucleus); Nucleus is the master
marketplace, while each plugin remains independently installable.
<!-- OPENAI-SUPPORT:END -->


## License

MIT. See `LICENSE`.
