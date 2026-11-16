---
type: llm
weight: 1
---

Judge only these points. Do not fail the response for leaving out other details.

1. The response gives a route plan that targets the `alignment` plugin (its Slack cross-team scan, pulse, or report).
2. The plan includes the route-plan fields: a target, the context it needs, a risk tier, a confidence, and a reason.
3. It does not run the Slack scan itself.
4. It does not make up specifics about team disagreements.

Pass if all hold. Fail if any one is violated.
