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
| `constitution/` | Rules that rarely change. Changing one needs an amendment (`/amend`). |
| `docs/requirements/` | What to build. Versioned (`v<N>-<date>.html`), with `register.yaml` as the list of every requirement ID. Change it with `/req`. |
| `docs/adr/` | One file per decision, numbered. Create with `/adr`. |
| `docs/architecture/` | Designs, versioned. |
| `planning/` | Backlog and roadmap. |
| `inputs/` | Received material (PRDs, notes, meetings, docs). Never edited. |
| `outputs/` | Guides and API references produced from the work. |
| `code/` | One folder per service or repo. |
| `.claude/` | Agents, commands, hooks, path-scoped rules and skills for this project. |

## Commands
- `{{dev command}}` — start locally
- `{{build command}}` — production build
- `{{test command}}` — tests
- `{{lint command}}` — lint

## How work flows here
1. A new or changed requirement → `/req` → new requirements version + register update.
2. A decision with alternatives → `/adr` → `docs/adr/NNNN-<slug>.md`, status Proposed until accepted.
3. A change to a constitution rule → `/amend` → entry in `constitution/AMENDMENTS.md`.
4. Code changes follow `constitution/` and `.claude/rules/`; `/pr-review` before merge.
5. End of a session with real progress → `/handoff`.

## Hooks (see `.claude/settings.json`)
- **session-start** — shows the latest requirements version, latest ADRs, and HANDOFF next steps.
- **prompt-router** — reminds Claude to run `/req` or `/adr` when a message adds requirements or makes a decision.
- **protect-published-versions** — blocks edits to any committed `docs/**/v<N>-<date>*` file.
- **git pre-commit** (`.githooks/`) — refuses commits made with an identity other than `.claude/git-identity`. Enable once per clone: `git config core.hooksPath .githooks`.

## Change log
- {{YYYY-MM-DD}}: created from the agent-engineering project template.
