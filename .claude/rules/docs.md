---
paths:
  - "docs/**"
  - "outputs/**"
---

# Documentation rules

- Versioned documents are `v<N>-<YYYY-MM-DD>.<ext>` in their own folder with an `index.html` or `README.md` listing versions newest first.
- A committed version is frozen (the protect-published-versions hook enforces it). Copy to the next version to change it.
- Every number carries a source, or is labelled as an assumption. Every other claim cites its source (file:line, commit, ticket, a named person and date) or is listed under Unknowns. Never invent product terms, SLAs or integration details.
- When code and docs disagree, the code is the truth and the doc is the bug: fix the doc in the same change.
- `inputs/` is raw input and is never edited.
- No top-level `*.md` status or summary files in a repo root; progress belongs in the ticket or the spec.

## Design and wording

- No AI-generated look: no emoji as icons, no rows of identical pastel cards with a centred icon, a bold word and a
  grey caption, no gradient hero covers, no coloured status chips scattered through the text. Design each document on
  purpose: diagrams specific to the content, a clear typographic hierarchy, real screenshots, tables and charts that
  carry information.
- No dashes as punctuation: no em dash, no en dash used as a pause, no double hyphen. Use a full stop, a comma, a
  colon or brackets, or rewrite the sentence. This covers body text, captions, tables and diagram labels.
- A document for an outside party (client, partner, regulator) carries no author name, no "confidential", "draft"
  or "pending" wording, and nothing about other customers, partners or markets it was not written for.
- Documents for outside parties are deep, not minimal: business, product and platform first, then components and
  third parties, then the technical parts from high level to low level (architecture with every business flow,
  infrastructure, operations, testing, security, data residency, performance, functional and non-functional
  requirements), then compliance. Each section has its visual. Read the specs and the code before writing; do not
  summarise from memory.
