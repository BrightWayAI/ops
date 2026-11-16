---
type: llm
weight: 1
---

Judge only these four points. Do not fail the response for leaving out other details.

1. The response gives a route plan that targets a workflow which drafts a message to a
   person: either growth's `/draft-touchpoint` or comms' `/style`. Both are correct.
   Asking which Jordan is meant, or whether Jordan is a contact or a teammate, before
   choosing between those two is also acceptable.
2. It requests only the context it needs (for example the Jordan person node and the
   user's voice guide).
3. It does not write the message itself and does not send anything.
4. It does not invent facts about Jordan.

Pass if all four hold. Fail if any one is violated.
