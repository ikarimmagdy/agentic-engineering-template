---
description: Show where a spec is in the loop and run its next step
argument-hint: [KEY]
---

Spec: $ARGUMENTS

1. Without a key: run `python3 tools/spec.py list` and show the table. Stop.
2. With a key: run `python3 tools/spec.py show <KEY>`.
3. Report in three lines: phase, what blocks it (from the output), the next command.
4. Ask whether to run that next command now. Do not run it without a yes.
