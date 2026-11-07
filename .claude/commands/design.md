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
6. Write `outputs/impact.json` from plan.md, data-model.md and contracts/: every component, flow (communication matrix row), infrastructure item, screen and use case this work adds, changes, removes or uses, with requirement ids, ADR numbers and the repo and path where each change lands (schema: `specs/README.md`, "System impact"). Reuse component ids from `repos.yaml` and `docs/architecture/baseline.json`. Run `python3 tools/impact.py check <KEY>`.
7. Run `python3 tools/spec.py check <KEY>`.
8. Owner approves: `tools/spec.py approve <KEY> design --by <name>`. Contracts are frozen from here.
9. Commit: `<KEY>: design`. Next: `/tasks <KEY>`.
