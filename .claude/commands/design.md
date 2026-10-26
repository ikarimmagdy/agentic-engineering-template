---
description: Phase 3 — design how the spec is built, across repos
argument-hint: <KEY>
---

Spec: $ARGUMENTS

1. Check the spec is approved. If not, stop.
2. Run the `architect` agent on spec.md, the gap analysis, `constitution/`, `docs/adr/` and the repos in `status.json`.
3. It writes `plan.md` (components per repo, sequence diagram, configuration names, flags, risks, rollout and rollback), `data-model.md`, and the OpenAPI / event schemas in `contracts/`.
4. Every real choice between alternatives becomes an ADR (`/adr`), linked from plan.md.
5. Draft `test-plan.md`: every acceptance criterion with its layer and planned test (status `planned`).
6. Run `python3 tools/spec.py check <KEY>`.
7. Owner approves: `tools/spec.py approve <KEY> design --by <name>`. Contracts are frozen from here.
8. Commit: `<KEY>: design`. Next: `/tasks <KEY>`.
