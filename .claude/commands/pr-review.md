---
description: Review the current branch, or a pull request, before merge
argument-hint: [PR URL | owner/repo#n]
---

PR: $ARGUMENTS

1. Diff the current branch against the main branch, or for a PR: `gh pr diff <n> -R <owner/repo>`.
2. Run the `code-reviewer` agent on it; run `security-auditor` too if auth, payments, data, secrets, networking or integrations changed.
3. Check every requirement ID mentioned in commits exists in `docs/requirements/register.yaml`.
4. For user-visible changes, confirm strings exist in every shipped language and, where the project uses flags, a feature flag gates the new behaviour. If a public API or contract changed, confirm its API doc changed in the same commit.
5. Run the `verify` skill, or confirm it ran green on this diff.
6. Report findings ranked by severity, then a merge / don't-merge verdict. Do not push, merge or move the ticket without the owner's go-ahead.
7. If the PR belongs to a spec (its branch, title or a `status.json` → `sources` entry names the spec key), append each finding to that spec's `outputs/findings.json` with `kind: defect`, `status: open`, `source: <PR URL>` and the fields listed in `/gap` step 7.
