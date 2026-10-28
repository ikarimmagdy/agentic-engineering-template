---
description: Root-cause a batch of customer or QA feedback against the code
argument-hint: <KEY> <pasted feedback, screenshots>
---

Spec and feedback: $ARGUMENTS

1. Number the reported issues F-1, F-2… exactly as the feedback describes them. Never copy names, phone numbers, emails, addresses or ID numbers from the text or screenshots.
2. Find the branch the reporter used (ask if unknown; default to the production branch in `outputs/review/scope.md`) and read the code path behind each issue. Evidence `repo:path:line` and `git blame` for when it was introduced.
3. Give each issue a verdict: **code** (confirmed), **code (likely)** (the path explains it, logs needed), **backend / data**, or **other** (environment, test data, configuration).
4. Link each issue to existing ids in `outputs/findings.json` when it is the same problem; add new findings for new defects (fields as in `/gap` step 7, `source` = the feedback file).
5. Write `outputs/feedback/v<N>-<YYYY-MM-DD>.md` (next free N): summary table, one section per issue (verdict, root cause, evidence, fix direction), unknowns.
Then classify the new rows: `python3 tools/findings.py classify <KEY>` (type, component, team).
6. Commit: `<KEY>: feedback batch <N>`.
