---
type: llm
weight: 1
---

The scenario has one `cloud` row and one row with no `Runs on` value, which must be
treated as `local-device`. Both tasks come back with no folders attached. A successful
response, following `/register-schedules` Step 4:

- Requests `requires_local_device=false` and no folders for `nightly-listen`, and
  `requires_local_device=true` with `folders=[<config-root>]` for `weekly-end-week`.
- Does NOT report `nightly-listen` as `failed: no-folder-binding`. An empty folder
  list is expected for a cloud row.
- Writes a registration record for `nightly-listen` with `runs_on: "cloud"`,
  `requires_local_device: false`, an empty `folders` list, and
  `binding: "unverified-until-first-receipt"` (the listing did not expose attached
  repositories), and says that the first succeeded run receipt is what proves the row
  can reach the config root.
- Reports `weekly-end-week` as `failed: no-folder-binding`, writes no record for it,
  and gives the "Require this computer" repair instruction.
- Uses state schema `1.1.0`.

A failing response fails the cloud row for missing folders, requests a device binding
for it, treats the row with no `Runs on` value as cloud, records the unbound
`weekly-end-week` task as registered, or claims the cloud row is fully verified.
