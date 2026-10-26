# specs/ — one folder per piece of work in flight

Every change that adds or alters behaviour gets a folder here, named
`<KEY>-<slug>/`, where `<KEY>` is the issue tracker key of the initiative or epic
(e.g. `PROJ-123-card-freeze/`). The folder carries the work through the loop:

```
Intent → Spec → Design → Build → Test → Deploy → Maintain ─┐
   ▲                                                       │
   └───────── incidents, metrics, review findings ─────────┘
```

| Phase | File | Command | Agent | Gate to leave the phase |
|---|---|---|---|---|
| Intent | `intent.md` | `/intent` | — | owner approves (`tools/spec.py approve <KEY> intent`) |
| Spec | `spec.md` | `/spec` | spec-writer, gap-analyst | every requirement has acceptance criteria; owner approves |
| Design | `plan.md`, `data-model.md`, `contracts/` | `/design` | architect, adr-writer | contracts written; owner approves |
| Build | `tasks.md` → code | `/tasks`, `/build` | — (`verify` skill) | every task done; `/pr-review` clean |
| Test | `test-plan.md`, `outputs/test-runs/` | `/test` | test-writer | every acceptance criterion has a passing test |
| Deploy | `outputs/release-notes.md` | `/deploy` | release-manager | smoke test passes in the target environment |
| Maintain | `outputs/runbook.md`, incidents | `/maintain`, `/fix-issue` | security-auditor | findings become a new intent |

`/feature <KEY>` shows where a spec is and runs the next step.

## Files

| File | What | Edited by |
|---|---|---|
| `intent.md` | Why, for whom, the outcome, how success is measured, what already exists | `/intent` |
| `spec.md` | Requirements with IDs, acceptance criteria (Given/When/Then), non-functional requirements | `/spec` |
| `plan.md` | How: components touched per repo, sequence, configuration, rollout and rollback | `/design` |
| `data-model.md` | Tables, columns, migrations, personal-data classification | `/design` |
| `contracts/` | OpenAPI and event schemas this work adds or changes | `/design` |
| `tasks.md` | Ordered tasks; one task = one branch = one pull request. **The Status column is the only place task status lives** | `/tasks`, `tools/spec.py task` |
| `test-plan.md` | Every acceptance criterion mapped to a test at a named layer | `/test` |
| `status.json` | Phase, approvals, tracker links, repos. Read by hooks, `tools/spec.py` and dashboards | `tools/spec.py` only |
| `inputs/` | PRDs, design exports, tracker snapshots, meeting notes. Received material, never edited | anyone |
| `outputs/` | Gap analyses, review reports, test runs, release notes, runbooks | commands and agents |

## Rules

- Start one with `python3 tools/spec.py new <KEY> <slug>`; never copy `_template/` by hand.
- Once a file's phase is approved it changes only with a row in its Change log and a fresh approval.
- `python3 tools/spec.py check` must pass before a phase moves on. CI can run the same command.
- When the work ships and has run cleanly, set the phase to `done`. The folder stays: it is the record.
