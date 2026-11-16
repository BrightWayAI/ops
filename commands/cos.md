---
description: Talk to your chief of staff. Natural-language front door for Nucleus — plans a route for Nucleus-domain or role-addressed work, then lets the parent validate and execute the selected installed workflow under the shared autonomy policy. Replaces nucleus-router.
---

# /cos

Resolve the installed plugin manifest set, then invoke the read-only
`chief-of-staff` agent (`agents/chief-of-staff.md`) with:

- the user's request verbatim;
- the installed workflow/role catalog;
- no memory contents unless entity or priority context is actually needed to
  disambiguate the route.

The agent returns a structured `route_plan`; it does not invoke the target. The
parent validates the plan against the installed catalog and executes it.

```yaml
route_plan:
  status: ready | ambiguous | unsupported
  intent: <short normalized intent>
  mode: single | parallel
  target:              # mode: single
    plugin: <installed plugin or null>
    workflow: <skill/command or null>
    role: <optional read-only role or null>
  required_context: [hot, entity-index, autonomy-policy, plugin-config]
  required_capabilities: [<logical capability names>]
  risk_tier: low | medium | high | never
  confidence: high | medium | low
  reason: <one sentence grounded in the catalog>
  question: <one disambiguating question only when status=ambiguous>
  workers:             # mode: parallel only; 2 to 4 entries
    - id: w1
      target: {plugin: <installed plugin>, workflow: <skill/command>}
      brief: <one sentence: exactly what to find or draft, and for which entity>
      output: <what to return, including the sources for each fact>
      required_context: [<only what this worker needs>]
      risk_tier: low
  assemble: <one sentence: how the parent combines the worker outputs>
  then:                # optional; steps that are not low risk, run after the main work
    - action: <what would be done, in plain words>
      target: {plugin: <installed plugin>, workflow: <skill/command>} | null
      risk_tier: medium | high
      why: <one sentence>
```

A plan without `mode` is `single`.

`then` is for the parts of a request that write, send, or change something. Use it in
either mode. A send is always its own `then` step at `high` risk, separate from drafting
the message: drafting is low risk and can be a worker or the main target; sending is
not. When no installed workflow performs the step (for example sending an email through
a mail connector), set `target: null` and still list it, so the user sees it and it is
never done as a side effect.

Execution rules:

1. `ambiguous` — the parent asks `question`; do not execute either candidate.
2. `unsupported` — name the missing plugin/capability and stop.
3. `ready` — verify the plugin and workflow are installed. Reject stale or
   invented targets.
4. Load only `required_context`: `hot` for current priorities, `entity-index`
   when a named person/client/project needs resolution, and the autonomy policy
   before any action. Do not load all of `hot.md` and `index.md` by default.
5. Apply the tier from the autonomy policy. `low`: narrate and execute. `medium`:
   show the whole batch once with its evidence and execute what the user accepts.
   `high`: preview the exact action and confirm immediately before each one. Never
   execute a `never` action. The plan's tier is the planner's estimate; if the
   workflow turns out to do something in a higher tier, the higher tier applies.
   If the user's policy still has the 1.0.0 shape (an `Ask first` section and no
   risk-tier sections), there is no medium tier: handle every `Ask first` item and
   anything a plan marks `medium` as `high`.
6. Report the workflow run, skipped capabilities, evidence, and output location.

## Parallel plans

Most requests need one workflow and get a `single` plan. A request gets a `parallel`
plan only when it needs two or more different workflows whose results do not depend on
each other, for example "prep me for tomorrow's Acme call" (the client's status, the
relationship history, and what memory holds on the account).

The rules for a parallel plan:

1. **Two to four workers.** If a request seems to need more, the plan covers the four
   that matter most and names what it left out in `reason`.
2. **Workers only read and draft.** Every worker is `low` risk. Anything that writes to
   memory, sends, or changes an external record is never a worker. It goes in `then`
   with its own tier and is handled after assembly, under the autonomy policy, with the
   review or approval that tier requires.
3. **Narrow briefs.** Each worker gets its own `brief`, its `output`, and the context
   named for it. It does not get the conversation, the other workers' briefs, or the
   user's whole request.
4. **Evidence comes back with the result.** A worker returns what it found or drafted
   with the source of each fact: a memory path, a record ID, a thread ID, a date.

Executing a parallel plan:

1. Validate every worker's target against the installed catalog. A worker whose target
   is not installed is dropped and reported; the rest still run.
2. Start the workers at the same time, each as a sub-agent given only its brief, its
   output description, and its named context. On a host that cannot run sub-agents in
   parallel, run them one after another; the result is the same.
3. A worker runs the read-and-draft steps of its workflow without prompting the user.
   If the workflow needs an answer only the user has, the worker returns the question
   instead of guessing.
4. Assemble one answer as `assemble` describes, with a section per worker. Keep each
   fact next to its source. Do not blend the outputs into prose that loses where a
   claim came from.
5. If two workers disagree, show both and say so. Do not pick one silently.
6. If a worker failed or returned nothing, say which part is missing and why. Never
   present a partial result as complete.
7. Ask any questions the workers returned, then offer the `then` steps one at a time
   under their tiers. Running the workers approves nothing in `then`.

Plain natural language in a Nucleus session may reach this workflow without
`/cos`, but only when it contains a Nucleus domain, installed role, or known
workflow signal. Generic conversation and generic "help" remain outside its
trigger boundary.

If no plugin covers the request, the agent says so and names the missing capability rather than improvising a workaround.

Routing is always resolved dynamically from the installed catalog's manifest
and command descriptions — no intent table is hardcoded here. As one example,
`clients`' `commands/sow.md` frontmatter covers "turn this proposal into an
SOW," "draft a statement of work," and "SOW amendment," so those utterances
route to `clients` `/sow` without any change needed in this file when a new
command like it is added.
