---
description: Brownfield check — what of this spec already exists in the code
argument-hint: <KEY>
---

Spec: $ARGUMENTS

1. Read the spec's `intent.md` and `spec.md` (whatever exists so far) and `status.json` → `repos`.
2. Run the `gap-analyst` agent with those requirements and the repos under `code/`.
3. Write its result to the spec's `outputs/gap-analysis.md`: one row per capability or requirement with state (built / partial / missing), evidence `repo:path:line`, and what would change.
4. Copy the summary into intent.md "What already exists" and the `Existing` column of spec.md.
5. List every repo it touched in `status.json` → `repos`.
6. **Architecture:** add an "Architecture" section to `outputs/gap-analysis.md` with the styles and patterns the existing code already uses and its architecture problems (skills `architecture-patterns`, `data-architecture`).
7. Commit: `<KEY>: gap analysis`.
