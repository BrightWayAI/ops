---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill, Task]
append_system_prompt: |
  Eval fixture — installed Nucleus plugin catalog. This run loads only the ops
  plugin, so treat the list below as the plugins and commands that are installed
  and available to route to. Nothing outside this list is installed.
  Their workflows cannot be executed in this run. After validating the route,
  end with the route plan itself (target, required_context,
  required_capabilities, risk_tier, confidence, reason) and do not execute it.
  - cortex (memory): /recall, /search, /remember, /morning, /listen, /end-day, /end-week
  - briefing (the daily brief, reviews, timeline): /brief, /review, /timeline, /dashboard, /plan-tomorrow
  - growth (relationships and pipeline): /relationships, /draft-touchpoint, /pre-call-brief, /pull-signals, /touchpoint
  - clients (client engagements after signature): /client-status, /project-setup, /sow, /review-deliverable
  - comms (voice-matched writing): /style (draft an email, message, post or doc in the user's voice), /style-review, /post (LinkedIn roundup post)
  - admin (time tracking and billing): /track-time, /invoices (drafts the monthly billing packet for approval)
  - research (news roundup candidates): /roundup
  - alignment (Slack cross-team scan): scan, pulse, /report
  - ops (this plugin): /cos, /status, /diagnose, /register-schedules
---

Ask Client Success for this week's Acme status.
