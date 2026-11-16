# Agent run log

Two files, both inside the config root, both append-only JSON Lines, both metadata only.

| File | Written by | Holds |
|---|---|---|
| `<config-root>/plugins/ops/agent-runs/<YYYY-MM>.jsonl` | the `SubagentStart` / `SubagentStop` hooks (`hooks/log_agent_run.py`), automatically | every sub-agent start and stop |
| `<config-root>/plugins/ops/agent-runs/notes.jsonl` | `/log-agent-run`, when a person or a parent workflow has a judgment to record | what the user did with an agent's output |

Before ops 0.21.0 there was one hand-written log at `~/.brightway-state/agent-log.jsonl`,
outside the config root. Nothing writes there now. `/agent-metrics` still reads it if it
exists, so old entries are not lost.

## Automatic entries (schema 2.0.0)

One line when a sub-agent starts and one when it stops:

```json
{"schema_version":"2.0.0","ts":"2026-11-16T22:57:15Z","event":"stop","agent":"cortex:verifier","agent_id":"a7eefe99a0b37114d","session_id":"f9456117-a30e-4925-9d10-af6df8d3cb70","actor_id":"sample-user","source":"hook"}
```

| Field | Notes |
|---|---|
| `ts` | UTC, when the hook ran |
| `event` | `start` or `stop` |
| `agent` | the agent's name as the host reports it; plugin agents are `plugin:agent` |
| `agent_id` | the host's ID for this one run; pairs a `start` with its `stop` |
| `session_id` | the session it ran in |
| `actor_id` | the Actor ID from `<config-root>/memory/me/identity.md`; `unresolved` if there is none. Never a guess. |
| `source` | `hook` |

Duration is the gap between a run's `start` and `stop` lines. A `start` with no `stop`
means the session ended first or the run was interrupted.

The logger writes nothing when the config root cannot be resolved or reached, and it
never creates a config root. It runs in the background, prints nothing, and always exits
0, so it cannot slow or break a session.

## Judgment entries (`notes.jsonl`)

What a hook cannot know: whether the output was any good.

```json
{"timestamp":"2026-11-16T14:32:00Z","actor_id":"sample-user","agent":"growth:relationships-director","parent_skill":"/pre-call-brief","confidence":"Medium","user_action":"iterated","notes":"missed recent activity"}
```

| Field | Required | Notes |
|---|---|---|
| `timestamp` | yes | ISO 8601 UTC |
| `actor_id` | yes | as above |
| `agent` | yes | same name the automatic log uses |
| `parent_skill` | yes | the command that used the agent; `manual` for a direct call |
| `confidence` | yes | what the agent reported: `High`, `Medium`, `Low` |
| `user_action` | yes | `accepted`, `iterated`, `overrode`, `abandoned`; `scheduled` for an unattended run |
| `notes` | no | 200 characters or fewer; prefix `BUG:`, `LIMITATION:`, or `UPSTREAM:` to make it searchable |

## Privacy

Both files record what ran, not what was said.

- **Never logged:** prompts, agent replies, file paths, contact or client names, message
  text, CRM data, memory content.
- **Logged:** agent and command names, timestamps, host IDs for the run and session, the
  Actor ID (an attribution slug, the same value that tags memory entries), and a short
  general note if a person writes one.

The folder is under `plugins/`, which syncs through the private repository only.

## Readers

`/agent-metrics` (counts, durations, acceptance), `/status` (recent activity), and the
weekly improvement review once it exists.
