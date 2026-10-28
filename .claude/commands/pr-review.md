---
description: Review the current branch, or a pull request, before merge
argument-hint: [PR URL | owner/repo#n]
---

PR: $ARGUMENTS

1. Diff the current branch against the main branch, or for a PR: `gh pr diff <n> -R <owner/repo>`.
2. Run the `code-reviewer` agent on it; run `security-auditor` too if auth, data, secrets or integrations changed.
3. Check every requirement ID mentioned in commits exists in `docs/requirements/register.yaml`.
4. Report findings ranked by severity, then a merge / don't-merge verdict.
5. If the PR belongs to a spec (its branch, title or a `status.json` → `sources` entry names the spec key), append each finding to that spec's `outputs/findings.json` with `kind: defect`, `status: open`, `source: <PR URL>` and the fields listed in `/gap` step 7.
