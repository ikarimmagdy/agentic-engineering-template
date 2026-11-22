---
description: Phase 4 — implement one task from tasks.md, tests first
argument-hint: <KEY> <task-id>
---

Task: $ARGUMENTS

1. Read the task row, the requirements and acceptance criteria it covers, plan.md and the contracts. Read the `.claude/rules/` file for every path you will touch.
2. In the task's repo under `code/<repo>/`, branch `<KEY>/<task-id>-<slug>` from the repo's main branch. `python3 tools/spec.py task <KEY> <task-id> doing`.
3. Write the failing tests first, named with the acceptance criterion ID (e.g. `..._AC_R1_1`), at the layer test-plan.md gives.
4. Implement the smallest change that makes them pass and follows the constitution and the contracts. Configuration by name only; values from `.env` or the secret store.
5. Run the `verify` skill for that repo (build, lint, unit and component tests). Then run the service in the local environment (`local-env/`) and exercise the change.
6. Update test-plan.md rows to `written` or `passing`. Keep `outputs/impact.json` true: set the `where` (repo, path, branch) of what this task changed, and add any flow, configuration name, table or screen the build added that the design did not foresee. `python3 tools/impact.py check <KEY>`.
7. **Code map:** when this task changes how the repos talk to each other (a new endpoint, client, topic or repo), refresh the Floorplan of the work item's repos and save it as the next `outputs/floorplan/v<N>-<date>.html` (copy of the generated `floorplan/index.html`, exported without its Health check and local paths; the `floorplan/` folder itself stays uncommitted), listed in `outputs/floorplan/README.md`. Follow the pattern's code shape and tests from `architecture-patterns` (outbox, idempotent consumer, circuit breaker).
8. Commit in the service repo with the task ID and acceptance criteria in the message. Push the branch and open a pull request only when the owner says so.
9. Run `/pr-review` on the branch. When clean: `tools/spec.py task <KEY> <task-id> review` (then `done` after merge).
