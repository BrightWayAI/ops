---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill, Task]
---

Dry run: the `nightly-listen` row in the definitions file has `Runs on` set to
`local-device`. Assume `create_trigger` for it returns a task id,
but the immediate `list_triggers` verification call shows that task with
`derived_state.folders_state == "NONE"` (no folders attached, `requires_local_device`
was not honored by the mock scheduler). Config root resolves to
`~/Documents/ClaudeCortex`. Walk `/register-schedules` Step 4 against this exact
scenario and tell me what it reports and what it writes to
`<config-root>/plugins/ops/schedule-registrations/<host-id>.json`.
