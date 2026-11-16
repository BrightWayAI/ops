---
description: Record what you did with a sub-agent's output (accepted, iterated, overrode, abandoned) and a short note. Sub-agent runs themselves are logged automatically; this adds the judgment a hook cannot know. Appends one line to <config-root>/plugins/ops/agent-runs/notes.jsonl.
---

# /log-agent-run

Lightweight telemetry. Records what just happened with a subagent call.

You don't need to log every agent run — only ones where the result was meaningfully better-or-worse than expected, or where a pattern is emerging. Over time, even sparse logging shows you which agents are pulling weight.

This command can be invoked by the user manually or by a parent skill (the latter being more common and more durable).

---

## Step 0 — Preflight

Every sub-agent start and stop is already recorded automatically by this plugin's hooks
(`references/agent-log-schema.md`). Use this command only to add a judgment: what the
user did with the output, and optionally why.

Resolve `<config-root>` the usual way. If it cannot be resolved or reached, say so and
stop; do not write the note anywhere else. The file is
`<config-root>/plugins/ops/agent-runs/notes.jsonl`, JSON Lines, append-only.

---

## Step 1 — Gather inputs

Either the parent skill passes the values directly, or (when invoked manually) prompt:

| Field | Value | Notes |
|---|---|---|
| `actor_id` | string | The Actor ID from `<config-root>/memory/me/identity.md`: the person this run acted for. Write `unresolved` if no identity exists; never guess. |
| `agent` | string | Which subagent was called (e.g., `relationships-director`, `pipeline-analyst`) |
| `parent_skill` | string | Which skill or command invoked the agent (e.g., `/relationships`, `/pre-call-brief`) |
| `confidence` | string | The Confidence rating the agent returned (`High`, `Medium`, `Low`) |
| `user_action` | string | What the user did with the output: `accepted`, `iterated`, `overrode`, `abandoned` |
| `latency_seconds` | int (optional) | Roughly how long the agent took |
| `notes` | string (optional) | One-liner — anything qualitative worth remembering |

Keep prompts brief. If the parent skill called this with all values, no prompts.

---

## Step 2 — Append the entry

Append one JSON Lines record to `<config-root>/plugins/ops/agent-runs/notes.jsonl`:

```json
{"timestamp":"2026-05-08T14:32:00Z","actor_id":"sample-user","agent":"relationships-director","parent_skill":"/pre-call-brief","confidence":"Medium","user_action":"iterated","latency_seconds":45,"notes":"Dossier missed recent LinkedIn activity"}
```

Use ISO 8601 UTC for timestamp.

If the file doesn't exist, create it. Never modify existing lines (append-only).

---

## Step 3 — Confirm

Quietly: "Logged."

Don't make a big deal of it. This is observability infrastructure, not a celebration.

---

## When parent skills should invoke this

Parent skills are the durable instrumenter. Add `/log-agent-run` calls (or equivalent inline-write logic) at these moments:

- **After the user acts on an agent's output** — record `user_action`
- **If the user goes silent and takes over manually** — record `abandoned`

Do not call this just to record that an agent ran; the hooks already do that.

The simplest pattern: the parent skill writes a single combined entry once the user has acted on the agent's output (so user_action is captured in the same line as everything else).

---

## When NOT to log

- Trivial agent calls. If you're invoking memory-librarian for routine `/search` queries, don't log every one — only the ones where confidence was unexpectedly Low or the result was surprising.
- High-volume scheduled runs. If note-taker processes many meetings, log one run receipt per scheduled run, not one entry per meeting.

A sparse, qualitative log beats a dense, mechanical one.

---

## Privacy

The log contains:
- ✅ Timestamps, agent names, skill names, confidence ratings, user actions
- ❌ Never: contact names, message content, CRM data, customer details

It's a *meta* log — what happened, not what the data was. Don't pipe content into it. If notes contain sensitive context, redact before logging.

---

## See also

- `/agent-metrics` — summarize the log over a time window
- `references/agent-log-schema.md` — schema documentation for the log file
