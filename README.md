# Agentic engineering workspace template

A workspace for building features with Claude Code the same way across a team: a spec for
every change, a test for every acceptance criterion, and the stack runnable on a laptop.

```
Intent → Spec → Design → Build → Test → Deploy → Maintain ─┐
   ▲                                                       │
   └───────── incidents, metrics, review findings ─────────┘
```

## Start a workspace from this template

```bash
git clone https://github.com/ikarimmagdy/agentic-engineering-template.git my-workspace
cd my-workspace
rm -rf .git && git init                      # your own history
git config core.hooksPath .githooks          # identity check on commit
```

Then fill in the placeholders (`{{...}}`):

1. `CLAUDE.md`: project name, what it is, tech stack, commands.
2. `.claude/git-identity`: the author email (or `@yourdomain`) commits must use.
3. `repos.yaml`: your organisation (`org:`) and the repos you work on, grouped.
4. `local-env/.env.example`: the configuration names your services need (values go in `local-env/.env`, never committed).
5. `constitution/`: keep P-1…P-7; add your product invariants and architecture rules.

## Keep a workspace up to date

The template keeps improving; a workspace inherits it with one command, run from the workspace:

```bash
tools/template-update.sh --dry-run    # what would change
tools/template-update.sh --adopt      # first time: carry the whole template ("full" mode)
tools/template-update.sh              # every time after
```

Only the paths in `tools/template-files.txt` belong to the template. A file still exactly as some template
version shipped it is replaced; a file you edited is three-way merged against the version recorded in
`.template-version`, or kept and listed when that is not possible. Files you added are never touched, and
`CLAUDE.md`, `constitution/`, `docs/`, specs and everything else that is yours are never read. Commit the result.
The workspace's Engineering Hub lives in `hub/` and comes with the template: `--adopt` adds a starter hub, and every
update moves its engine (from the template's `hub/`, itself built from `engineer-hub-template`) while `hub/content/`,
the hub's own data, stays as it is. Template maintainers bump `VERSION` with every change.

## Where the code is

`code/` is empty in a fresh clone on purpose. Each service stays in its own repository and is
cloned next to the specs:

```bash
bin/clone --list           # repos and groups from repos.yaml
bin/clone core             # clone one group into code/<name>/
bin/clone --all
GIT_HOST=my-ssh-alias bin/clone mobile   # an ~/.ssh/config host alias
```

`code/*/` is gitignored, so the workspace repo holds the specs, rules and tools, and each
service repo keeps its own history, branches and pull requests.

## Your first feature

```text
/intent PROJ-123 card-freeze <idea | Jira key | GitHub issue | PR URL>
/gap PROJ-123          # if existing code is involved
/spec PROJ-123
/design PROJ-123
/tasks PROJ-123
/build PROJ-123 T1
/test PROJ-123
/feature PROJ-123      # where it is, and the next step
```

Each step writes into `specs/PROJ-123-card-freeze/` and stops for an approval before the next
phase (`python3 tools/spec.py approve`). `examples/data-addon/` walks through the whole loop.

## What is in here

| Path | What |
|---|---|
| `CLAUDE.md` | The project brain Claude reads first |
| `.claude/` | Commands (the loop), agents, hooks (spec gate, published versions, prompt router), rules, skills |
| `constitution/` | Process invariants and rules; changed only through `/amend` |
| `specs/` | One folder per piece of work; `specs/_template/` and `specs/README.md` |
| `docs/` | Requirements, ADRs, architecture (`baseline.json` for the system map) |
| `tools/` | `spec.py` (phases and gates), `findings.py`, `impact.py` (system impact), `hub_check.py` |
| `local-env/`, `tests/` | Local stack and cross-service tests (api, mobile, e2e) |
| `repos.yaml`, `bin/clone`, `code/` | The service repos and where they are cloned |

The Engineering Hub reads a workspace made from this template:
https://github.com/ikarimmagdy/engineer-hub-template
