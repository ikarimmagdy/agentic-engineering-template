---
description: Write (or read) the resume state so the next session or teammate can continue
argument-hint: [read]
---

Mode: $ARGUMENTS

- `read`: show `HANDOFF.md` (Goal, State, Next, Blockers) and `python3 tools/spec.py list`. Stop.
- Otherwise update `HANDOFF.md`:
  1. **Updated:** today's date.
  2. **State:** what is true now — specs and their phases, what was built or decided this session, with paths.
  3. **Next:** the next concrete steps, each runnable by someone who was not here (command or file).
  4. **Blockers:** what waits on whom.
  5. Keep it under 40 lines; details live in the specs.
  6. Commit: `handoff: <one line>`.
