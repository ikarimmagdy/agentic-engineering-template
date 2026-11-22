---
description: Brownfield check and code review by area — what of this spec already exists in the code, and what is wrong with it
argument-hint: <KEY> [area|all]
---

Spec and area: $ARGUMENTS

Areas: `scope`, `architecture`, `infra`, `apis`, `data`, `localization`, `ui-ux`, `security`, `tests`. No area means the capability map only (steps 1 to 5); `all` runs every area.

1. Read the spec's `intent.md` and `spec.md` (whatever exists so far) and `status.json` → `repos`.
2. Run the `gap-analyst` agent with those requirements and the repos under `code/`.
3. Write its result to the spec's `outputs/gap-analysis.md`: one row per capability or requirement with state (built / partial / missing), evidence `repo:path:line`, and what would change.
4. Copy the summary into intent.md "What already exists" and the `Existing` column of spec.md.
5. List every repo it touched in `status.json` → `repos`.
6. For each area asked, review the code against the checklist below and write `outputs/review/<area>.md`: what was read (repo, branch, commit), what was found, evidence `repo:path:line`. Always write `outputs/review/scope.md` with the repos, branches and commits read.
7. **Architecture:** add an "Architecture" section to `outputs/gap-analysis.md` with the styles and patterns the existing code already uses and its architecture problems (skills `architecture-patterns`, `data-architecture`): synchronous calls to slow outside systems in a request path, a component reading another component's tables, outside calls without timeout, retry and circuit breaker, a database change and an outside message that can drift apart, retried work that is not idempotent. Each problem is also a finding in the `architecture` area (step 8).
8. Append every finding to `outputs/findings.json` (create it if missing: `{"version": 1, "key", "generated", "sources": [], "findings": []}`) as one row:
   `{"id", "title", "layer", "category", "dimension", "area", "severity", "scope", "kind", "location", "detail", "impact", "fix", "status", "source"}`
   - `area`: the area being reviewed; `layer`: the app, service or repo the finding is in (e.g. ios, android, web, api, a service name);
   - `severity`: critical | high | medium | low; `dimension`: security | functional | reliability | performance | maintainability | release;
   - `kind`: `gap` (the PRD asks for it, the code does not do it) or `defect` (the code does it wrong); `scope`: new feature code vs legacy if known, else null;
   - `status`: open; `source`: the review file path; `title` ≤ 90 characters. Update `generated` and `sources`.
   Ids stay stable: never renumber an existing finding.
   Then classify the new rows: `python3 tools/findings.py classify <KEY>` (type, component, team).
9. Commit: `<KEY>: gap analysis` or `<KEY>: review <area>`.

## Area checklists

**localization**
- iOS: every `.localized()` key and `NSLocalizedString` key exists in both `ar` and `en` `Localizable.strings`; no orphan keys.
- Android: every key in `values/strings.xml` exists in `values-ar/strings.xml`; no `tools:ignore="MissingTranslation"` hiding gaps.
- Hard-coded user-facing strings in code, layouts, storyboards and XIBs.
- Raw server messages or codes shown to users (e.g. a `-401` code inside an alert) instead of a mapped, translated message.
- Notifications (SMS, push, email) sent without a language, or with templates missing in one language.
- RTL: layout direction, alignment, mirrored icons, text fields and phone/number inputs.
- Arabic-Indic digits: input converted before validation and API calls; display consistent.
- Currency and VAT formatting per locale; dates and plural rules.
- PRD and Figma copy against the strings actually shipped.
- The translation management system in use: keys present in the app but missing in the TMS, and the reverse.

**architecture**: components and their responsibilities, call paths per PRD step, where each business rule lives (client vs server), duplicated logic across platforms, coupling to legacy.
**infra**: where each service runs (Kubernetes cluster, VMs, serverless, other), deploy files and pipelines in the repo, configuration and secrets handling, environments, health checks.
**apis**: endpoints the feature uses, authentication and authorisation per endpoint, idempotency, error mapping, versioning, contracts against callers.
**data**: tables and migrations, personal data stored and where, retention, caches on device or server.
**ui-ux**: every PRD and Figma step against the screens, states (loading, empty, error), back navigation, accessibility, error messages per PRD outcome.
**security**: authorisation and ownership checks, secrets in code, sensitive data in logs, transport security, webhook signatures.
**tests**: which flows have unit, component, API, mobile and end-to-end tests; what the PRD needs that nothing tests.
