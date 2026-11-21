---
description: Phase 1 — start a piece of work from a PRD, epic or idea and write its intent
argument-hint: <KEY> <slug> [PRD link | tracker key | file]
---

Input: $ARGUMENTS

1. If `specs/<KEY>-*` does not exist, run `python3 tools/spec.py new <KEY> <slug> --title "<title>"`.
2. Collect the sources into the spec's `inputs/` as dated files, never edited afterwards:
   - a PRD page: read it with the documentation MCP (e.g. Confluence) and save it as markdown;
   - a tracker key: read the initiative, its epics and stories with the issue-tracker MCP (e.g. Jira) and save a snapshot table (key, type, status, summary, parent);
   - designs: frame links and exported images from the design MCP (e.g. Figma).
   Record them: `python3 tools/spec.py link <KEY> --initiative <K> --epic <K> --story <K> --source <url>` (repeat flags as needed).
3. Write `intent.md` from the sources only: problem, who, outcome, success measures, scope, constraints. Anything the sources do not say goes under Open questions, never invented.
4. If existing code is involved, run `/gap <KEY>` to fill "What already exists".
5. **Diagrams:** write the phase's diagrams to `outputs/diagrams/intent/v<N>-<date>.md` (`specs/README.md`, "Diagrams"): the idea on one page (problem, who, value, scope in and out, success measures, risks) and the context (users, our system, outside systems). Draw only what the documents say.
6. Show the intent to the owner. When they approve: `python3 tools/spec.py approve <KEY> intent --by <name>` then `python3 tools/spec.py phase <KEY> spec`.
7. Commit: `<KEY>: intent`.
