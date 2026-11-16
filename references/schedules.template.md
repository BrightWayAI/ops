# Schedule Library — Starter

_Copy this immutable starter to `<config-root>/plugins/ops/schedules.md`, then
customize the user-owned copy. The installed plugin directory is read-only at runtime._

## Schedule Table

| Name | Cron / Schedule | Action | Plugin Required | Owner | Required/Optional | Runs on | Notes |
|---|---|---|---|---|---|---|---|
| nightly-listen | daily 23:00 (11pm) | `/listen` | cortex | self | Required | cloud | Unattended ingest with a post-06:00 stale-trigger guard. Stages proposals and refreshes `hot.md`; never writes durable nodes directly. |
| weekly-end-week | Friday 16:00 (4pm) | `/end-week` | cortex | self | Optional | local-device | Optional weekly review, cleanup, and reflection. |
| weekly-roundup | Friday 07:00 | `/roundup` | research | self | Optional — only relevant if research is installed | local-device | Stages cited roundup candidates; run comms's `/post` to draft. |

## Portability rules

- Keep definitions here free of scheduler IDs and machine names.
- `/register-schedules` stores per-host IDs under
  `<config-root>/plugins/ops/schedule-registrations/`.
- Every unattended prompt includes its run-window guard, permission behavior,
  expected output, and metadata-only receipt path.
- Remove or comment out schedules you do not use. Removing a row does not silently
  delete an already-registered host task.
- **`Runs on` says where the task executes.** Every row reads or writes
  `<config-root>`, so every row must be able to reach it. There are two ways.
  - `cloud` — the task runs as a cloud routine with no device attached. It reaches the
    config root by bootstrapping the two sync repositories at the start of the run
    (`cortex_cli.py bootstrap`) and publishing at the end (`sync`). It registers with
    `requires_local_device=false` and no folders, and runs whether or not any computer
    is on. Use it only for a workflow that documents a cloud contract; `/listen` does
    (cortex 4.29+). Pair it with a local `cortex_cli.py sync` job so the copy on your
    computer follows.
  - `local-device` — the task runs on the specific computer the registering
    conversation is linked to. It registers with `requires_local_device=true` and
    `folders=[<config-root>]`; that computer must be online with the Claude desktop app
    running at fire time. `/register-schedules` verifies the binding after every
    create/update via `list_triggers` and refuses to record a registration whose
    `derived_state.folders_state == NONE`.
- A row with no `Runs on` value (a definitions file written before this column
  existed) is treated as `local-device`, so existing registrations keep their binding
  and their fingerprint.
- Do not register the same schedule twice, once per mode. Two tasks doing the same
  ingest waste a run and can race on the same day's output.
- The definition fingerprint includes `requires_local_device` and `folders`, so
  changing a row from `local-device` to `cloud` (or back) classifies it as `changed`
  and the preview states that the old task will be replaced.
