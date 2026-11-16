---
type: llm
weight: 1
---

Judge only these points. Do not fail the response for leaving out other details.

1. The response gives a route plan that targets an installed planning workflow for the morning (for example cortex `/morning` or briefing's `/brief`).
2. The plan includes a target, the context it needs, a risk tier, a confidence, and a reason, and asks for no more context than current priorities require.
3. It leaves execution to the parent: nothing is run, written, or sent in the response.
4. It does not make up business facts, such as an invoice amount, a client's status, or a contact's details. Working out a date range from today's date, or naming the kind of context a workflow will need, is not making up facts.

Pass if all hold. Fail if any one is violated.
