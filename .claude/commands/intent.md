---
description: Phase 1 — start a piece of work from an idea, a tracker key, a GitHub issue or a pull request and write its intent
argument-hint: <KEY> <slug> <idea text | tracker key | owner/repo#issue | PR URL>
---

Input: $ARGUMENTS

1. Decide the intake kind from the input (`specs/README.md`, "Intake"):
   - **idea**: free text, no ticket. KEY is the tracker key it will live under, or the next free `IDEA-<n>` when there is no ticket yet (ask if unsure).
   - **tracker**: an initiative, epic or story key in the issue tracker the workspace uses (e.g. Jira, Linear, GitHub Projects).
   - **github-issue**: `owner/repo#<n>` or an issue URL.
   - **pr**: a pull request URL or `owner/repo#<n>` that is a PR.
2. If `specs/<KEY>-*` does not exist, run `python3 tools/spec.py new <KEY> <slug> --title "<title>" --intake <kind> --ref <ref>`; otherwise `python3 tools/spec.py intake <KEY> <kind> --ref <ref> --summary "<one line>"`.
3. Save the raw source into the spec's `inputs/` as a dated file, never edited afterwards:
   - idea: the text as given, with who gave it and when;
   - tracker: read the item and its children with the issue-tracker MCP and save a snapshot table (key, type, status, summary, parent); a linked product document is read with the documentation MCP and saved as markdown;
   - github-issue: `gh issue view <n> -R <owner/repo> --json number,title,body,labels,state,author,createdAt,comments` saved as markdown;
   - pr: `gh pr view <n> -R <owner/repo> --json number,title,body,headRefName,baseRefName,files,commits,author,url` saved as markdown, then run `/pr-review` on it so its findings land in `outputs/findings.json`;
   - designs: frame links and exported images from the design MCP (e.g. Figma), or exported images and links when no design tool is connected.
   Record links: `python3 tools/spec.py link <KEY> --initiative <K> --epic <K> --story <K> --source <url>` (repeat flags as needed).
4. Write `intent.md` from the sources only: problem, who, outcome, success measures, scope, constraints. Anything the sources do not say goes under Open questions, never invented.
5. If existing code is involved, run `/gap <KEY>` to fill "What already exists" and the review areas.
6. **Diagrams:** write the phase's diagrams to `outputs/diagrams/intent/v<N>-<date>.md` and list the version in that folder's `README.md` (`specs/README.md`, "Diagrams"): the idea on one page (problem, who, value, scope in and out, success measures, risks) and the context (users, our system, outside systems). Draw only what the documents say.
7. Show the intent to the owner. When they approve: `python3 tools/spec.py approve <KEY> intent --by <name>` then `python3 tools/spec.py phase <KEY> spec`.
8. Commit: `<KEY>: intent`.
