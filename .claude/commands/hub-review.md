---
description: Review work items (and the code they touch) against the rules the Engineering Hub relies on, and bring them in line
argument-hint: [KEY ... | all]
---

Review: $ARGUMENTS (no argument: every work item)

The hub shows each work item phase by phase: documents a section at a time, the diagrams of each phase in its Visual
mode and inside the sections they explain, a code map from build on, and nothing that only works on one laptop. This
command finds what an existing work item is missing for that and fixes it, the same way the phase commands would have
written it.

1. Run `python3 tools/hub_check.py <keys>` and show the result per work item: errors first, then warnings by rule.
2. For each work item with findings, propose the fixes below and ask before writing. A work item someone else started
   (`started_by` in status.json) needs their go-ahead too. Never edit a committed `v<N>-<date>` file: write the next
   version and add it to the folder's README.
   - **paths** (error; publishing refuses it): replace the laptop path with a path relative to the document, or a name;
     in HTML, link the stylesheet relatively or inline it.
   - **diagrams**: run the Diagrams step of the phase command for each phase listed (`specs/README.md`, "Diagrams"),
     from that phase's documents and the code only; an unknown is a node marked `?`.
   - **kinds**: start each diagram title with its kind (`Sequence: ...`, `Pattern: ...`, `States: ...`), so the hub
     places it in the section it explains.
   - **index**: add the folder's `README.md`, versions newest first, one line each on what changed (`.claude/rules/docs.md`).
   - **sections**: split the document into `## ` sections (Markdown) or `<h2>` sections (HTML), content unchanged.
   - **design**: run the `architect` agent (skills `architecture-patterns`, `data-architecture`) to add "Architecture
     choices" to plan.md from the existing design, ADRs and code: what was chosen, the alternatives, why, the
     constitution rules it relies on. No decision changes; a real choice not yet recorded becomes a proposed ADR
     (`/adr`). Add a Change log row saying the section records existing decisions.
3. **Existing code** (work items in build or later): run the `gap-analyst` architecture check on the item's repos
   (the styles and patterns the code already uses, and where it breaks them: synchronous calls to slow outside
   systems, cross-component table access, outside calls without timeout, retry and circuit breaker, a database write
   and an outside message that can drift apart, retried work that is not idempotent). Add each problem to the
   "Architecture" section of `outputs/gap-analysis.md`, write `outputs/review/architecture.md` and
   `outputs/review/scope.md`, and append each problem to `outputs/findings.json` in the `architecture` area (`/gap` step 8). This command never edits code: a fix becomes a task through `/tasks`.
4. Build or later without `outputs/floorplan/`: offer to make the code map of the item's repos (`/build`, "Code map").
5. Commit each work item's folder on its own: `<KEY>: hub review (<rules fixed>)`, then pull with rebase and push, as
   `tools/spec.py` shares a work item.
6. Run `python3 tools/hub_check.py <keys>` again and report what is left and why.
