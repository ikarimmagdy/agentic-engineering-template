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
| `outputs/impact.json` | What this work changes in the system, as data: components, flows (communication matrix), infrastructure, screens, use cases, decisions, each with `change` and `where`. Merged across specs into the system model by `tools/impact.py` | `/design` writes it, `/build` and `/deploy` keep it true |

## System impact (`outputs/impact.json`)

Every piece of work records what it changes, so the system picture grows with each story
(`python3 tools/impact.py json` merges all of them over `docs/architecture/baseline.json`; the
Engineering Hub shows it per work item and as the system map in Knowledge).

```json
{
  "version": 1, "key": "TELCO-2586", "updated": "2026-11-06",
  "summary": "One paragraph: what this work changes in the system.",
  "components": [{ "id": "Selfcare", "change": "changed", "summary": "...", "where": [{ "repo": "Selfcare", "path": "src/...", "ref": "TELCO-2586/T2-..." }] }],
  "flows": [{ "from": "vm-selfcare-ios", "to": "vm-selfcare-proxy", "protocol": "HTTPS/REST", "interface": "POST /api/v1/mnp/otp", "change": "added", "summary": "...", "reqs": ["R1"] }],
  "infra": [{ "id": "Selfcare.MNPDetails.OtpChannel", "kind": "column", "name": "MNPDetails.OtpChannel", "component": "Selfcare", "env": ["dev", "uat", "prd"], "change": "added", "summary": "..." }],
  "screens": [{ "id": "mnp-otp-channel", "name": "Choose OTP channel", "app": "vm-selfcare-ios", "platforms": ["ios", "android"], "change": "added", "summary": "...", "image": "outputs/review/ui-ux/x.jpg", "reqs": ["R2"] }],
  "useCases": [{ "id": "UC-1", "name": "Port in with an OTP over WhatsApp", "actor": "Customer", "change": "added", "summary": "...", "reqs": ["R1"], "components": ["vm-selfcare-ios", "Selfcare"] }],
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

## Rules

- Start one with `python3 tools/spec.py new <KEY> <slug>`; never copy `_template/` by hand.
- Once a file's phase is approved it changes only with a row in its Change log and a fresh approval.
- `python3 tools/spec.py check` must pass before a phase moves on. CI can run the same command.
- When the work ships and has run cleanly, set the phase to `done`. The folder stays: it is the record.
