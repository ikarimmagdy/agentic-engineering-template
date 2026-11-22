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
| `status.json` | Phase, approvals, intake, tracker links, repos. Read by hooks, `tools/spec.py` and dashboards | `tools/spec.py` only |
| `inputs/` | PRDs, design exports, tracker snapshots, meeting notes. Received material, never edited | anyone |
| `outputs/` | Gap analyses, review reports, test runs, release notes, runbooks | commands and agents |
| `outputs/review/<area>.md` | Code review of the existing code per area: `scope`, `architecture`, `infra`, `apis`, `data`, `localization`, `ui-ux`, `security`, `tests` | `/gap <KEY> <area>` |
| `outputs/findings.json` | Every finding as data: `id`, `title`, `layer`, `category`, `dimension`, `area`, `severity`, `scope`, `kind` (gap / defect), `location`, `detail`, `impact`, `fix`, `status`, `source`. Ids never renumbered | `/gap`, `/pr-review`, `/feedback` |
| `outputs/feedback/v<N>-<date>.md` | One customer or QA feedback batch: verdict and root cause per issue, linked to finding ids | `/feedback` |
| `outputs/impact.json` | What this work changes in the system, as data: components, flows (communication matrix), infrastructure, screens, use cases, decisions, each with `change` and `where`. Merged across specs into the system model by `tools/impact.py` | `/design` writes it, `/build` and `/deploy` keep it true |
| `outputs/diagrams/<phase>/v<N>-<date>.md` | The phase as pictures: Mermaid diagrams chosen for that phase (below). The hub's Visual mode shows them | every phase command |
| `outputs/floorplan/v<N>-<date>.html` | A Floorplan map of the work item's repos: parts, files, endpoints and the requests between them, across repos | `/build` |

## System impact (`outputs/impact.json`)

Every piece of work records what it changes, so the system picture grows with each story
(`python3 tools/impact.py json` merges all of them over `docs/architecture/baseline.json`; the
Engineering Hub shows it per work item and as the system map in Knowledge).

```json
{
  "version": 1, "key": "PROJ-123", "updated": "2026-11-06",
  "summary": "One paragraph: what this work changes in the system.",
  "components": [{ "id": "cards-service", "change": "changed", "summary": "...", "where": [{ "repo": "cards-service", "path": "src/...", "ref": "PROJ-123/T2-..." }] }],
  "flows": [{ "from": "mobile-app", "to": "api-gateway", "protocol": "HTTPS/REST", "interface": "POST /api/v1/cards/{id}/freeze", "change": "added", "summary": "...", "reqs": ["R1"] }],
  "infra": [{ "id": "cards-service.cards.frozen_at", "kind": "column", "name": "cards.frozen_at", "component": "cards-service", "env": ["dev", "uat", "prd"], "change": "added", "summary": "..." }],
  "screens": [{ "id": "card-freeze", "name": "Freeze card", "app": "mobile-app", "platforms": ["ios", "android"], "change": "added", "summary": "...", "image": "outputs/review/ui-ux/x.jpg", "reqs": ["R2"] }],
  "useCases": [{ "id": "UC-1", "name": "Freeze a lost card", "actor": "Customer", "change": "added", "summary": "...", "reqs": ["R1"], "components": ["mobile-app", "cards-service"] }],
  "decisions": ["0023"]
}
```

- `change`: `added`, `changed`, `removed`, or `used` (touched on the path, not modified).
- Component ids: the repo `name` from `repos.yaml`, or an id from `docs/architecture/baseline.json`
  (external systems, data stores). A component in neither carries `name`, `layer` and `kind` on its entry.
- `where`: repo, path (file or folder), and the branch or tag (`ref`) where the change is.
- `infra.kind`: `database`, `table`, `column`, `stored-procedure`, `config`, `secret`, `queue`,
  `topic`, `cache`, `job`, `k8s`, `ingress`, `certificate`, `dns`, `feature-flag`, `other`.
- `python3 tools/impact.py check [KEY]` validates it; `spec.py check` requires it from the build phase on.

## Intake

Every spec records where it came from in `status.json` → `intake` (`python3 tools/spec.py intake <KEY> <kind> --ref <ref>`):

| Kind | Ref | Read with |
|---|---|---|
| `idea` | none | the text as given |
| `jira` | initiative, epic or story key | issue-tracker MCP (Jira), PRD through the documentation MCP (Confluence) |
| `github-issue` | `owner/repo#n` | `gh issue view` |
| `pr` | PR URL | `gh pr view`, then `/pr-review` |

## Rules

- Start one with `python3 tools/spec.py new <KEY> <slug>`; never copy `_template/` by hand.
- Once a file's phase is approved it changes only with a row in its Change log and a fresh approval.
- `python3 tools/spec.py check` must pass before a phase moves on. CI can run the same command.
- When the work ships and has run cleanly, set the phase to `done`. The folder stays: it is the record.

## Diagrams (`outputs/diagrams/`)

Each phase explains itself in pictures as well as in documents. The phase command writes
`outputs/diagrams/<phase>/v<N>-<date>.md` (phase: `intent`, `spec`, `design`, `build`, `test`, `deploy`,
`maintain`): a short Markdown file, one `## <diagram title>` per diagram, a one-line caption saying what to read
from it, then one ` ```mermaid ` block. Draw only from the phase's documents and the code, never invented; a fact
that is not known yet is a node marked `?`. Start each title with its kind (`Containers`, `Sequence: <flow>`, `Data model`, `Deployment`, `Pattern: <name>`,
`States: <entity>`, `Journey: <name>`, `Requirement map`): the hub places each diagram in the section of the phase's document
that it explains (Sequence in "Sequence", Data model in "Data") and groups the rest by kind. Like every `v<N>-<date>` file, a version is frozen once committed: a
rerun writes the next version.

| Phase | Diagrams |
|---|---|
| intent | **The idea on one page** (problem, who, value, scope in and out, success measures, risks, as a `mindmap` or a `flowchart` of cards); **context** (users, our system, outside systems: `flowchart` or C4 context) |
| spec | **Requirement map** (requirements → acceptance criteria, grouped by story); **a flow per user journey** (`flowchart`); **states** for every entity with a status (`stateDiagram-v2`) |
| design | **Containers** (C4 container: apps, proxy, gateway, services, stores, brokers, providers); **a sequence per contract** (`sequenceDiagram`); **data model** (`erDiagram`); **deployment** (clusters, namespaces, environments); **the chosen patterns** (event flow, saga states, outbox, before and after routing: `architecture-patterns`) |
| build | **Task dependencies** (`flowchart` of tasks.md); **what changed where** (components and repos from `impact.json`); the code map is the Floorplan (`outputs/floorplan/`) |
| test | **Coverage by layer** (criteria per layer, passing and failing); **the test path** of the main journey |
| deploy | **Deploy order** across repos, with migrations and flags; **promotion** DEV → UAT → PROD with the checks between; **rollback** |
| maintain | **Runbook flow** (symptom → check → action); **incident timeline** since release |

