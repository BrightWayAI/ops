---
type: llm
weight: 1
---

Judge only these four points. Do not fail the response for leaving out other details.

1. Registration: the prompt includes a sentence naming actor `sample-user` to be
   recorded as `actor_id` in the receipt, and the registration record stores
   `registered_by: sample-user`.
2. Unreachable root: the receipt has a failed outcome with `config_root_unreachable`,
   and the actor comes from the registered prompt (`sample-user`, source
   `registration`), not from a guess.
3. No identity: registration stops and the user is sent to `/setup-identity`; a
   schedule is not registered without an accountable actor, and no actor is invented.
4. Old receipt: `outcome: "success"` is accepted as success, and the missing actor is
   treated as not recorded rather than as a failure.

Pass if all four hold. Fail if any one is violated.
