---
description: Break an approved design into tasks, one pull request each
argument-hint: <KEY>
---

Spec: $ARGUMENTS

1. Check the design is approved.
2. Write `tasks.md`: one row per task small enough for one pull request (about a day), with repo, the requirement / acceptance criteria it covers, its tracker story, dependencies, status `todo`. Contracts and migrations come first, then services, then apps, then end-to-end tests.
3. Every acceptance criterion is covered by at least one task.
4. If the tracker should carry sub-tasks, list them for the owner; create them with the issue-tracker MCP only when told to.
5. `python3 tools/spec.py phase <KEY> build` (the gate checks the approvals).
6. Commit: `<KEY>: tasks`.
