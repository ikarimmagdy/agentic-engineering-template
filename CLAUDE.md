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
| `specs/<KEY>-*/outputs/diagrams/<phase>/`, `outputs/floorplan/` | Each phase in pictures: versioned Mermaid diagrams every phase command writes (`specs/README.md`, "Diagrams"), titles starting with their kind; the Floorplan code map of the work item's repos from `/build`. The Engineering Hub shows them in each phase's Visual mode and inside the sections they explain. |
| `.claude/skills/architecture-patterns/`, `.claude/skills/data-architecture/` | How the `architect` (and `gap-analyst`) chooses an architecture: communication styles, integration and resilience patterns, where data lives, each with its diagram and tests. Fill their "Where we use it" columns with this system's `repo:path`. |
| `tools/hub_check.py`, `/hub-review` | Check work items against the rules the Engineering Hub relies on (phase diagrams, diagram kinds, version indexes, no laptop paths, sectioned documents, architecture choices) and bring existing ones in line. |
| `usage/agent-runs/` | Agent-run counts people chose to share (per day, agent and count only), written by the hub's `tools/share_usage.py --push`; the hub's Home adds them up. Created on first share. |
| `.claude/` | Agents, commands, hooks, path-scoped rules and skills for this project. |
| `examples/` | Worked example of the loop (data add-on), one file per step. Reference only. |

## Commands
- `{{dev command}}` — start locally
- `{{build command}}` — production build
- `{{lint command}}` — lint
- Tests by layer: unit `{{…}}` · component `{{…}}` · functional `{{…}}` · api `{{…}}` · mobile `{{…}}` · e2e `{{…}}`
- `python3 tools/spec.py list | show <KEY> | check` — where every spec is
- `python3 tools/impact.py check [KEY] | json | show <component>` — what each spec changes in the system
- `python3 tools/hub_check.py [KEY ...]` — work items against the hub's rules; `/hub-review [KEY|all]` brings them in line

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
- Work items written before these rules, or a workspace adopting the hub → `/hub-review all`: phase diagrams, sections, version indexes, architecture choices, and the code's architecture findings.

## Hooks (see `.claude/settings.json`)
- **session-start** — shows specs in flight, the latest requirements version, latest ADRs, and HANDOFF next steps.
- **prompt-router** — points Claude at the right command (`/intent`, `/spec`, `/adr`, `/build`, `/test`, `/deploy`, `/fix-issue`) when a message matches.
- **protect-published-versions** — blocks edits to any committed `docs/**/v<N>-<date>*` file.
- **spec-gate** — blocks edits under `code/` unless a spec is in the build phase with intent, spec and design approved (`SPEC_GATE=off` for a recorded emergency fix).
- **git pre-commit** (`.githooks/`) — refuses commits made with an identity other than `.claude/git-identity`. Enable once per clone: `git config core.hooksPath .githooks`.

## Change log
- {{YYYY-MM-DD}}: created from the agent-engineering project template.
- 2026-11-22: each phase in pictures (`outputs/diagrams/<phase>/`, every phase command's Diagrams step, titles by kind), Floorplan code map in `/build`, architecture skills `architecture-patterns` and `data-architecture` with the architect's decision procedure and `/gap` architecture checks, `tools/hub_check.py` and `/hub-review` to bring existing work in line, `usage/agent-runs/` for shared agent counts (Engineering Hub template 5.12 to 5.18).
