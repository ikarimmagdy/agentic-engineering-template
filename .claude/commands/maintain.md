---
description: Phase 7 — run what shipped; feed what is learned back into the loop
argument-hint: <KEY>
---

Spec: $ARGUMENTS

1. Write or update `outputs/runbook.md`: what runs where, dashboards, alerts, logs, known failure modes and the fix for each, owner.
2. Collect what happened since release: incidents, errors, metrics against the intent's success measures, review and security findings.
3. Defects → `/fix-issue`. Security findings → `security-auditor`, then `/fix-issue`.
4. New needs → a new intent (`/intent <NEW-KEY> …`) that links this one. Never reopen a done spec for new scope.
5. When the success measures are met and nothing is open: `tools/spec.py phase <KEY> done`.
