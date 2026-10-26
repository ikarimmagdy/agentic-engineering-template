# L1 — Invariants

Rules that hold for the life of the project. Breaking one is a defect, not a trade-off.
Change only through `/amend`.

## How work is done

These come with the template. A project may amend them; it should not drop them silently.

| ID | Invariant | Why |
|---|---|---|
| P-1 | No code change without a spec in the build phase whose intent, spec and design are approved. Production fixes go through `/fix-issue` and are recorded. | Agents build what is written; unwritten intent gets invented. |
| P-2 | Every acceptance criterion is proved by an automated test at the lowest layer that can prove it, named with the criterion ID. | A criterion without a test is a wish. |
| P-3 | Contracts (OpenAPI, event schemas) change in the same commit as the code that implements them. | Consumers build against the contract, not the code. |
| P-4 | No secret value in any tracked file. Configuration is referenced by name; values come from a local `.env` or the secret store. | Repositories are copied, forked and indexed. |
| P-5 | Every phase change and approval is recorded through `tools/spec.py` (status.json). | Status is read by people and dashboards; it must not drift. |
| P-6 | Before existing behaviour changes, the gap analysis records what exists, with file:line evidence. | Brownfield code holds rules nobody wrote down. |
| P-7 | Received material in `inputs/` is never edited. | Every decision must trace back to what was actually asked. |

## Product invariants

| ID | Invariant | Why |
|---|---|---|
| I-1 | {{e.g. Every state-changing action is audited before it returns}} | {{reason}} |
