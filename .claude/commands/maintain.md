---
description: Phase 7 — run what shipped; feed what is learned back into the loop
argument-hint: <KEY>
---

Spec: $ARGUMENTS

1. Write or update `outputs/runbook.md`: what runs where, dashboards, alerts, logs, known failure modes and the fix for each, owner.
2. Collect what happened since release: incidents, errors, metrics against the intent's success measures, review and security findings.
3. **Diagrams:** write the phase's diagrams to `outputs/diagrams/maintain/v<N>-<date>.md` and list the version in that folder's `README.md` (`specs/README.md`, "Diagrams"): the runbook flow (symptom → check → action) and the incident timeline since release. Draw only what the documents say.
4. Defects → `/fix-issue`. Security findings → `security-auditor`, then `/fix-issue`.
5. New needs → a new intent (`/intent <NEW-KEY> …`) that links this one. Never reopen a done spec for new scope.
6. When the success measures are met and nothing is open: `tools/spec.py phase <KEY> done`.
