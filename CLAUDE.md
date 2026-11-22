# {{PROJECT_NAME}} — project brain

{{ONE_PARAGRAPH: what this project is, who it is for, and the one thing it must never get wrong.}}

Personal and workspace rules come from the parent CLAUDE.md files. This file
covers only this project. Anything stated about how this project works is
recorded here in the same turn.

## Tech stack
- {{frontend}}
- {{backend}}
- {{database}}
- {{hosting}}

## Where things live
| Path | What |
|---|---|
| `specs/` | One folder per piece of work in flight, `<KEY>-<slug>/`: intent, spec, design, tasks, test plan, status. See `specs/README.md`. |
| `constitution/` | Rules that rarely change, including the process invariants P-1…P-7. Changing one needs an amendment (`/amend`). |
| `docs/requirements/` | Product-wide requirements. Versioned (`v<N>-<date>.html`), with `register.yaml` as the list of every requirement ID. Change it with `/req`. |
| `docs/adr/` | One file per decision, numbered. Create with `/adr`. |
| `docs/architecture/` | Designs, versioned. |
| `planning/` | Backlog and roadmap across specs. |
| `inputs/` | Received material for the project as a whole. Never edited. (Per-feature inputs live in the spec.) |
| `outputs/` | Guides and API references produced from the work. |
| `code/` | One folder per service or repo. |
| `local-env/` | Run everything locally: dependencies, mocks, services, local Kubernetes, `.env.example`. |
| `tests/` | Cross-service tests: `api/`, `mobile/`, `e2e/`. Unit, component and functional tests stay in each repo. |
| `specs/<KEY>-*/outputs/impact.json`, `docs/architecture/baseline.json` | What each piece of work changes in the system; `tools/impact.py json` merges them into the system model (Engineering Hub: Impact tab and System map). |
| `tools/spec.py` | Creates specs, moves phases with gates, updates tasks, checks, exports JSON. |
| `.claude/` | Agents, commands, hooks, path-scoped rules and skills for this project. |
| `examples/` | Worked example of the loop (data add-on), one file per step. Reference only. |

## Commands
- `{{dev command}}` — start locally
- `{{build command}}` — production build
- `{{lint command}}` — lint
- Tests by layer: unit `{{…}}` · component `{{…}}` · functional `{{…}}` · api `{{…}}` · mobile `{{…}}` · e2e `{{…}}`
- `python3 tools/spec.py list | show <KEY> | check` — where every spec is
- `python3 tools/impact.py check [KEY] | json | show <component>` — what each spec changes in the system

## How work flows here
```
Intent → Spec → Design → Build → Test → Deploy → Maintain → (back to Intent)
```
1. A PRD, epic or idea → `/intent <KEY> <slug> <source>`; existing code → `/gap <KEY>`. Owner approves.
2. `/spec <KEY>` → requirements with IDs and Given/When/Then criteria. Owner approves.
3. `/design <KEY>` → plan, data model, contracts, test plan; choices → `/adr`. Owner approves.
4. `/tasks <KEY>` → one task per pull request; then `/build <KEY> <task-id>` for each, tests first.
5. `/test <KEY>` → every criterion passing, layer by layer.
6. `/deploy <KEY> <env>` → release notes, pipeline, smoke test.
7. `/maintain <KEY>` → runbook, incidents, `/fix-issue`; new needs become a new intent.
- `/feature [KEY]` shows where things are and runs the next step.
- Product-wide requirement → `/req`. Constitution change → `/amend`. Before merge → `/pr-review`. End of session → `/handoff`.

## Hooks (see `.claude/settings.json`)
- **session-start** — shows specs in flight, the latest requirements version, latest ADRs, and HANDOFF next steps.
- **prompt-router** — points Claude at the right command (`/intent`, `/spec`, `/adr`, `/build`, `/test`, `/deploy`, `/fix-issue`) when a message matches.
- **protect-published-versions** — blocks edits to any committed `docs/**/v<N>-<date>*` file.
- **agent-log** — records each subagent start and end in `.claude/state/agent-runs.jsonl` (gitignored; agent, description, spec key, never the prompt) for the Engineering Hub's Agents view.
- **Work items are shared at every gate**: `tools/spec.py` new, intake, link, approve, phase and task commit that work item's `specs/<KEY>-*/` folder, pull with rebase and push. Session start warns about unpushed work items and team commits not pulled. `SPEC_SHARE=local` commits without pushing.
- **spec-gate** — blocks edits under `code/` unless a spec is in the build phase with intent, spec and design approved (`SPEC_GATE=off` for a recorded emergency fix).
- **git pre-commit** (`.githooks/`) — refuses commits made with an identity other than `.claude/git-identity`. Enable once per clone: `git config core.hooksPath .githooks`.

## Change log
- {{YYYY-MM-DD}}: created from the agent-engineering project template.
