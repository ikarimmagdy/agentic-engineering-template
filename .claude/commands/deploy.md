---
description: Phase 6 — release a spec to an environment
argument-hint: <KEY> <environment>
---

Release: $ARGUMENTS

1. Confirm the target environment and that the owner asked for this deploy.
2. `python3 tools/spec.py phase <KEY> deploy` must succeed (every acceptance criterion passing). Without a key, run the full test suite instead and stop on any failure.
3. Run the `release-manager` agent: order of deploys across repos (plan.md → Rollout), migrations, flags, configuration present in the target, rollback steps. It writes `outputs/release-notes.md`.
4. Confirm no published document version or accepted ADR is contradicted by what ships.
5. Deploy through the project's pipeline (see CLAUDE.md → Commands / Deploy). Never deploy from a laptop to a shared environment.
6. Smoke-test the deployed environment and report the result with the URL. Set `env` on the `infra` entries of `outputs/impact.json` to include the environment just deployed, and `ref` to the released tag.
7. After production: `tools/spec.py phase <KEY> maintain`.
