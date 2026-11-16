# Security Policy

## What this plugin does with your data

Ops (Ops) is the shared toolkit plugin: hosts the `chief-of-staff` agent (`/cos`), `/diagnose` (ecosystem health), telemetry (`/log-agent-run`, `/agent-metrics`), and the schedule library (`/register-schedules`). As of 2026-09-15, the `pipeline-analyst` and `pipeline-forecast` CRM subagents live in the `growth` plugin; `/cos` delegates to them there when growth is installed, and shows "Growth not installed; pipeline analysis skipped" otherwise.

**Reads:**
- **Plugin references** — immutable templates and schemas in `references/`.
- **Agent run log** — `<config-root>/plugins/ops/agent-runs/` (read by `/agent-metrics` and `/status`).
- **Shared private profile** — `<config-root>/memory/me/identity.md` (read-only).
- **Cortex memory** (if installed) — for `/diagnose` to verify cortex initialization status. Read-only.

**Writes:**
- **Plugin settings** — `<config-root>/plugins/ops.user-context.md` (after `/setup-core`).
- **Schedule definitions/state/receipts** — `<config-root>/plugins/ops/`; installed references are never mutated.
- **Agent run log** — `<config-root>/plugins/ops/agent-runs/`. The plugin's `SubagentStart` and `SubagentStop` hooks append one metadata line each time a sub-agent starts or stops (`<YYYY-MM>.jsonl`); `/log-agent-run` appends judgment notes (`notes.jsonl`). Both are append-only.
- **Cowork scheduled tasks** — `/register-schedules` registers entries with Cowork's scheduled-tasks system, with explicit user confirmation per registration.

**Does not:**
- **Access the CRM directly.** Pipeline subagents (read-only) now live in the `growth` plugin.
- **Auto-register schedules.** Always shows the list and waits for "y" before any registration.
- **Modify the agent log.** Append-only by design; `/agent-metrics` is strictly read-only.
- **Log message content or sensitive data** — the agent run log captures only meta-records (which agent ran, when, in which session, for which actor, and optionally what the user did with the output). Prompts, replies, and file paths are never recorded. See `references/agent-log-schema.md` for the explicit privacy guidance.
- **Run scheduled tasks.** Only registers them; execution is owned by Cowork's scheduled-tasks system.

## Where data lives

- Immutable plugin reference files inside the installed plugin directory.
- User settings and schedule state under `<config-root>/plugins/ops/`.
- Agent run log at `<config-root>/plugins/ops/agent-runs/`. This folder is inside the config root's `plugins/` directory, so it syncs to your own private repository along with your other plugin settings. It is metadata only. (Before ops 0.21.0 the log was at `~/.brightway-state/` and never left the machine.)
- Shared identity (read-only) at `<config-root>/memory/me/identity.md`.

## What gets sent off your machine

- Nothing CRM-related — this plugin no longer talks to the CRM directly (see the `growth` plugin's `pipeline-analyst` / `pipeline-forecast` for that).
- The agent log never leaves your machine — it's a local observability file.

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a vulnerability

Report privately via GitHub Security Advisories:

https://github.com/BrightWayAI/core-ops/security/advisories/new

Do not open a public issue for security concerns. We aim to respond within 5 business days.
