---
name: verify
description: Run this project's full verification — build, typecheck, lint, tests — and report pass/fail per step. Use before committing a code change or claiming something works.
---

1. Read the Commands section of `CLAUDE.md` for this project's build, lint and test commands. If it has none, take them from the repo being changed: its `README.md`, `package.json`, `Makefile`, `pom.xml`/`build.gradle` or `pyproject.toml`.
   If none are documented anywhere, say so; do not invent a gate.
2. Run each in order. Stop at the first failure and show its output.
3. Report a table: step, command, result.
4. Never report success for a step you did not run. If no command exists for a step, say so.
