---
description: Phase 5 — prove every acceptance criterion, layer by layer
argument-hint: <KEY> [layer]
---

Spec: $ARGUMENTS

1. Read test-plan.md and `.claude/rules/testing.md`.
2. For every acceptance criterion without a test, run the `test-writer` agent at the layer named in the plan.
3. Run the layers in order and stop at the first failure: `unit` → `component` → `functional` → `api` → `mobile` → `e2e`. The commands for each layer are in CLAUDE.md → Commands. Functional, api, mobile and e2e need the local environment running (`local-env/`).
4. Save each run to `outputs/test-runs/<date>-<layer>.md`: command, commit, result, failures.
5. Update each row's status in test-plan.md (`passing` / `failing`).
6. **Diagrams:** write the phase's diagrams to `outputs/diagrams/test/v<N>-<date>.md` and list the version in that folder's `README.md` (`specs/README.md`, "Diagrams"): coverage by layer (criteria per layer, passing and failing) and the test path of the main journey. Draw only what the documents say. Include the pattern tests the design names (compensation paths, idempotency, contract and schema tests).
7. `python3 tools/spec.py check <KEY>`. When every task is done and every criterion has a test: `tools/spec.py phase <KEY> test`; when every criterion is passing it can move to deploy.
8. Commit: `<KEY>: test run <date>`.
