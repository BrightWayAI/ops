---
description: Register user-owned schedule definitions from the shared config root with an available host scheduler. Keeps immutable plugin defaults separate from per-host registration IDs and run receipts. Useful on first setup, a new machine, or after a scheduler reinstall. Creates real scheduled tasks and always requires confirmation.
---

# /register-schedules

Provision standing schedules from user-owned definitions. The installed plugin is
read-only at runtime: bundled references are defaults, never mutable state.

## State contract

- Definitions: `<config-root>/plugins/ops/schedules.md`
- Bundled starter: `references/schedules.template.md`
- Per-host registration state:
  `<config-root>/plugins/ops/schedule-registrations/<host-id>.json`
- Metadata-only run receipts:
  `<config-root>/plugins/ops/schedule-runs/<schedule>/<run-id>.json`

`<host-id>` is a stable, non-secret identifier such as
`cowork-macbook-pro` or `codex-desktop`. Never put host-specific IDs in the
definition file or installed plugin directory.

## Step 0 — Resolve and initialize

Before doing anything else, tell the user how each row will run. Each definition has
a `Runs on` value (see `references/schedules.template.md`); a row without one is
`local-device`.

- For `local-device` rows: (1) the computer must be awake (not asleep) at the
  scheduled run time, (2) the first unattended run will prompt for tool-use approvals
  — approve each with "always allow" so later runs don't stall on a prompt nobody is
  watching, and (3) **the row is bound to this specific computer** — the task fires
  from the Mac this registering conversation is linked to, and that Mac must be online
  with the Claude desktop app running at fire time, or the run is silently skipped
  until the next scheduled window.
- For `cloud` rows: the task runs with no computer attached. It reaches the config
  root by bootstrapping the two sync repositories at the start of every run and
  publishing at the end, so both repositories must be attached to the routine and the
  local copy only updates when a local `cortex_cli.py sync` job runs.

Resolve `<config-root>` using the shared precedence chain: explicit override,
`CORTEX_CONFIG_ROOT`, `~/.cortex/config-root` (primary), legacy pointer
`~/Documents/.claude-plugin-config-root` (fallback), then default.

Every schedule registered by this command reads or writes `<config-root>` — there is
no schedule in the library today that doesn't — so every registration must prove the
task can reach it, in the way its `Runs on` value implies:

- `local-device`: Step 4 MUST request `requires_local_device=true` and
  `folders=[<config-root absolute path>]` (the resolved absolute path, not a
  placeholder). This is what makes "Require this computer" + the folder attachment
  happen at creation time instead of leaving the task able to fire on a device that
  can never reach `<config-root>`.
- `cloud`: Step 4 MUST request `requires_local_device=false` with no folders, and the
  registered prompt MUST begin with the bootstrap step and end with the publish step
  of the target workflow's cloud contract. Only register a row as `cloud` when its
  workflow documents one (`/listen` does). Otherwise report the row as
  `unavailable: no-cloud-contract` and leave it unregistered.

Never register the same definition in both modes. If the live scheduler already has
an enabled task for the same schedule in the other mode, show both in the Step 3
preview and ask which one to keep.

If the definitions file is missing, preview the bundled starter and offer to copy it
to the definitions path. If the user declines, return the path and stop. Never edit
`references/schedules.template.md` or `references/schedules.md` at runtime.

By default, only register `nightly-listen` — it is the one required schedule.
`weekly-end-week` and `weekly-roundup` (the latter only if `research` is installed)
are available in the starter but not auto-registered; mention them and offer to
register either if the user wants them.

Detect `scheduler.register`. If unavailable, validate and return the definitions for
manual setup without claiming registration.

## Step 1 — Validate definitions and dependencies

Parse each enabled row:

- `name` — unique kebab-case identifier
- `schedule` — cron or host-readable schedule
- `action` — installed workflow to invoke
- `plugin` — owning plugin
- `owner` — normally `self`
- `runs_on` — `cloud` or `local-device`; missing means `local-device`
- `notes` — guardrails and expected output

Reject duplicate names, missing fields, retired plugins/actions, or dependencies that
are not installed. A missing optional plugin skips that row; it does not invalidate
the rest of the library.

Compute a definition fingerprint from normalized
`name + schedule + action + plugin + requires_local_device + folders`, where a
`cloud` row contributes `requires_local_device=false` and an empty folder list.
Including the binding fields means an already-registered task that predates them
classifies as `changed` on the next run and gets re-registered correctly, and so does
a row whose `Runs on` value was edited. A `local-device` row's fingerprint is the same
as before the `Runs on` column existed, so existing registrations stay `current`.

## Step 2 — Reconcile with this host

Read this host's registration-state file if present. When the scheduler can list
existing tasks, reconcile against live state; live state wins over the cache.

Classify each definition:

- `new` — no matching live task or state record
- `current` — live task and fingerprint match
- `changed` — name matches but fingerprint differs
- `missing-live` — cached ID exists but scheduler no longer has it
- `unavailable` — dependency or scheduler capability missing

Never skip solely because a cached ID exists. Never register a duplicate solely
because a state file is absent.

## Step 3 — Preview and confirm

Show new, changed, skipped, and current schedules, including exact action and timing.
Ask once for explicit confirmation before any create/update call. Changed schedules
must state whether the host will update in place or replace the old task.

## Step 4 — Register and persist state

For each confirmed `new`, `changed`, or `missing-live` entry:

1. Call `create_trigger` (or the host's equivalent). For a `local-device` row set
   `requires_local_device=true` and `folders=[<config-root>]` explicitly — never omit
   these fields, even for `changed` entries that are only being re-registered to pick
   up the binding. For a `cloud` row set `requires_local_device=false`, attach no
   folders, and attach the two sync repositories named in
   `<config-root>/.cortex-repos.json`.
2. Capture returned ID and scheduler name.
3. **Verify the binding actually took.** Call `list_triggers` and find the
   just-created or just-updated task by its returned id.

   For a `cloud` row require that the task is enabled and has no device requirement.
   An empty folder list is expected and is not a failure. If the listing shows the
   task's attached repositories, require both sync repositories; if it does not expose
   them, record `"binding": "unverified-until-first-receipt"` and say so in the output.
   A cloud row's reachability is proven by its first succeeded run receipt, not by
   registration. If the task is missing or still device-bound, report
   `failed: cloud-registration-not-applied` and write no record.

   For a `local-device` row require both:
   - `derived_state.folders_state != NONE`
   - the resolved `<config-root>` absolute path is present in `derived_state.folders`
   If either check fails, do **not** write a registration-state record for this
   entry. Report it as `failed: no-folder-binding` with this exact instruction:
   "open the task in the Claude desktop app on the linked Mac, turn on 'Require this
   computer', attach `<config-root>`, then re-run `/register-schedules --verify`."
   Treat this the same as any other per-row failure — continue reconciling the rest
   of the library.
4. On a successful verification, atomically update only this host's
   registration-state JSON, and stamp `last_verified_at` to now.
5. Continue after individual failures and record a sanitized error code.

State schema:

```json
{
  "schema_version": "1.1.0",
  "host_id": "cowork-macbook-pro",
  "scheduler": "cowork",
  "updated_at": "2026-11-16T18:00:00-05:00",
  "registrations": {
    "nightly-listen": {
      "scheduler_id": "opaque-host-id",
      "definition_fingerprint": "sha256:...",
      "runs_on": "cloud",
      "requires_local_device": false,
      "folders": [],
      "binding": "verified",
      "registered_by": "sample-user",
      "registered_at": "2026-11-16T18:00:00-05:00",
      "last_verified_at": "2026-11-16T18:00:00-05:00"
    },
    "weekly-end-week": {
      "scheduler_id": "opaque-host-id",
      "definition_fingerprint": "sha256:...",
      "runs_on": "local-device",
      "requires_local_device": true,
      "folders": ["<config-root absolute path>"],
      "binding": "verified",
      "registered_at": "2026-11-16T18:00:00-05:00",
      "last_verified_at": "2026-11-16T18:00:00-05:00"
    }
  }
}
```

Schema `1.1.0` adds `runs_on` and `binding`. A `1.0.0` record has neither; read it as
`runs_on: "local-device"`, `binding: "verified"`, and rewrite it as `1.1.0` the next
time that entry is updated.

Write atomically. Schedule IDs are machine-specific operational metadata, not source
configuration and not portable between hosts.

## Step 4.5 — `--verify` mode

`/register-schedules --verify` re-runs only the Step 4 binding checks (folder binding
for `local-device` rows, the cloud checks for `cloud` rows) against this host's
already-registered live tasks — it never creates, updates, or deletes a
task. For each registration in this host's state file:

1. `list_triggers`, find the task by its stored `scheduler_id`.
2. Not found live → classify `missing-live`; do not update `last_verified_at`; report
   it in the output so a plain `/register-schedules` run can re-create it.
3. Found, a `local-device` row, but `derived_state.folders_state == NONE` or
   `<config-root>` absent from `derived_state.folders` → leave the registration-state record as-is (don't erase
   history) but report `failed: no-folder-binding` with the same repair instruction
   as Step 4, and do NOT bump `last_verified_at`.
4. Found, a `cloud` row → never fail it for an empty folder list. Require that it is
   enabled with no device requirement. If its record says
   `unverified-until-first-receipt` and a succeeded receipt for that schedule now
   exists, set `binding` to `verified`.
5. Found and bound correctly → update only `last_verified_at` for that entry.

This mode is read-only against the scheduler aside from the `list_triggers` call and
the local `last_verified_at` bump — no `create_trigger`/`update_trigger` call is ever
made in `--verify`. `ops`'s `/status` command calls this mode read-only (it does not
invoke registration) to render the SCHEDULED LOOP section.

## Step 5 — Scheduled-run receipts

Every registered prompt must request one metadata-only receipt per run. Schema
`1.1.0` (ops 0.17.0) adds the accountable actor and settles the outcome spelling:

```json
{
  "schema_version": "1.1.0",
  "run_id": "<host run id or UUID>",
  "schedule": "nightly-listen",
  "actor_id": "<Actor ID the run acts for>",
  "actor_source": "identity | registration | unresolved",
  "host_id": "cowork-macbook-pro",
  "started_at": "<ISO-8601>",
  "ended_at": "<ISO-8601>",
  "outcome": "succeeded | partial | skipped | failed",
  "source_coverage": {"calendar": "read|skipped|failed"},
  "outputs": [{"path": "<config-root-relative path>", "sha256": "..."}],
  "error_codes": []
}
```

- **`actor_id` is required.** It names the person the run acts for, who is accountable
  for what it stages. It is the `Actor ID` from `<config-root>/memory/me/identity.md`.
  `actor_source` says where the value came from: `identity` (read from that file at run
  time), `registration` (the identity file could not be read, so the actor named in the
  registered prompt was used), or `unresolved` (neither was available). An unresolved
  receipt has `actor_id: "unresolved"` and the `actor_unresolved` error code. A run never
  guesses or invents an actor.
- **Every registered prompt names its actor.** At registration, read the Actor ID from
  the identity file and include this sentence in the prompt: "This run acts for actor
  `<actor-id>`; record that as `actor_id` in the run receipt." If no identity exists,
  stop and send the user to `/setup-identity`; do not register a schedule with no
  accountable actor. Record the same value as `registered_by` in the registration state.
  The definition fingerprint does not cover the prompt text, so a registration made
  before 0.17.0 (no `registered_by`) stays `current` and keeps working: its runs still
  resolve the actor from the identity file. List such a row as
  `current (prompt does not name an actor)` and offer to update its prompt. Updating a
  task is a schedule change and needs the user's approval like any other.
- **`outcome`** is one of `succeeded`, `partial`, `skipped`, `failed`. Readers also
  accept the 1.0.0 spellings (`outcome: "success"`, or `status: "succeeded"` /
  `status: "failed"` with a singular `error_code`).
- Where cortex is installed, write receipts with
  `python3 scripts/cortex_cli.py write-receipt` (cortex 4.36.0+), which resolves the
  actor, validates the outcome, and prints the receipt to stdout if the file cannot be
  written.

Receipts contain no connector payloads, messages, transcript text, credentials, or
memory content. If the target workflow cannot write a receipt on the active host, say
so during preview and rely on host scheduler history instead.

Every registered prompt must keep the existing run-window guard (skip a catch-up run
outside its intended window rather than firing stale) and the receipt requirement
above, and MUST additionally include this instruction verbatim as part of what gets
registered: "If `<config-root>` is not readable, write nothing, emit a receipt with
`status=failed` and `error_code=config_root_unreachable`, and exit non-zero. Do not
report success." (The wording of that sentence is unchanged so existing
registrations keep their fingerprint; a 1.1.0 writer emits `outcome: "failed"` with
`error_codes: ["config_root_unreachable"]`, which readers treat as the same thing.) This is what turns an unreachable config root (e.g. a task that
fired on the wrong device, or a Mac where the folder was detached) into a loud,
visible failure instead of a scheduler-reported "success" that did nothing. For a
`cloud` row the same instruction applies after the bootstrap step: if bootstrap cannot
materialize the root, the run fails loudly the same way.

## Output

Report counts for current, registered, updated, skipped, and failed entries; list IDs
only for the current host; and state where registration state and run receipts live.
Do not claim success for rows that were merely returned as manual definitions.

## Behavior rules

- Installed plugin directories are immutable at runtime.
- Definitions are portable; registration state is per-host.
- Live scheduler state wins over cached IDs.
- Registration and changes always require confirmation.
- Failures are explicit and do not prevent independent rows from continuing.
- Removing a definition does not silently unregister its live task; surface it as an
  orphan and ask before deletion.

## What this is not for

- One-off reminders or meetings.
- External cron provisioning when the active host exposes no scheduler.
- Automatic unregistration or destructive scheduler cleanup.
