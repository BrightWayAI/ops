---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill, Task]
---

Dry run: the definitions file has two rows. `nightly-listen` has `Runs on` set to
`cloud`. `weekly-end-week` has no `Runs on` value. Assume `create_trigger` returns a
task id for each. The immediate `list_triggers` call shows the `nightly-listen` task
enabled, with no device requirement and `derived_state.folders_state == "NONE"`, and
does not show which repositories are attached. It shows the `weekly-end-week` task
with `derived_state.folders_state == "NONE"` as well. Config root resolves to
`~/cortex-root`. Walk `/register-schedules` Step 4 against this exact scenario and
tell me what it requests for each row, what it reports, and what it writes to
`<config-root>/plugins/ops/schedule-registrations/<host-id>.json`.
