# Evals

Run from the repository root:

```
claude plugin eval . --ablation none --judge-model sonnet
```

An eval run loads only this plugin, and a case cannot load plugins from outside this
repository. The seven routing cases therefore carry an `append_system_prompt` that lists
the installed sibling plugins and their commands, and asks the run to end with the route
plan instead of executing it. They test the routing decision only. They do not test that
the parent executes a route.

Keep the catalog in those cases in step with the real plugins when a sibling adds,
renames or removes a command the router should know about.

Use `--judge-model sonnet`. With the default judge, the long `register-schedules` cases
were graded inconsistently on identical-quality answers.
