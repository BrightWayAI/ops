---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Dry run: load the `/cos` instructions with the Skill tool (loading them runs nothing),
then tell me how execution rule 5 applies to these three `ready` route plans. Do not
execute anything.

A. `cortex` `/recall` for the Acme node, `risk_tier: low`.
B. A workflow that merges six overnight memory proposals that all passed verification
   and conflict with nothing, `risk_tier: medium`.
C. `admin` `/invoices` sending this month's billing packet with three invoices,
   `risk_tier: high`.

Then tell me what changes for B if my autonomy policy still has the old `Ask first`
section and no risk-tier sections.
