---
description: Phase 2 — turn the approved intent and the stories into a testable spec
argument-hint: <KEY>
---

Spec: $ARGUMENTS

1. Check the intent is approved (`python3 tools/spec.py show <KEY>`). If not, stop and say so.
2. Run the `spec-writer` agent on the intent, `inputs/` (PRD, stories, designs) and `outputs/gap-analysis.md`.
3. It writes `spec.md`: one requirement per row with ID `<KEY>-R<n>` and its tracker story, Given/When/Then acceptance criteria `AC-R<n>.<m>`, non-functional requirements, data and privacy, localisation, analytics, notifications.
4. Anything a story or the PRD does not settle goes to intent.md Open questions, not into the spec as a guess.
5. If a requirement contradicts `constitution/` or an accepted ADR, stop and say which.
6. Run `python3 tools/spec.py check <KEY>`. Fix what it reports.
7. **Diagrams:** write the phase's diagrams to `outputs/diagrams/spec/v<N>-<date>.md` and list the version in that folder's `README.md` (`specs/README.md`, "Diagrams"): the requirement map (requirements → criteria, by story), a flow per user journey, and a state diagram for each entity with a status. Draw only what the documents say.
8. Show the spec to the owner. On approval: `tools/spec.py approve <KEY> spec --by <name>` then `tools/spec.py phase <KEY> design`.
9. Commit: `<KEY>: spec`.
