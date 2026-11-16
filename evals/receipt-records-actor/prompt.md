---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Dry run: load the `/register-schedules` instructions with the Skill tool (loading them
runs nothing), then answer from Step 5 without executing anything.

1. I'm registering `nightly-listen`. My identity file has Actor ID `sample-user`. What
   goes into the registered prompt and the registration record about who the run acts
   for?
2. Tonight's run cannot read the config root at all. What does its receipt say about
   the actor and the outcome?
3. A different install has no identity file. What happens when that user tries to
   register a schedule?
4. An old receipt says `"outcome": "success"` and has no actor field. How should a
   reader treat it?
