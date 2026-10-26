# 10 — Documentation: `doc-writer`

**Loop step:** write the guides people use, from the code and requirements, versioned. **Agent:** `doc-writer`. **Where:** `outputs/developer-guide/`, `outputs/api/`, `outputs/product-guide/`.

## What the engineer types

> Use doc-writer: developer guide v1 for the data add-on flow (audience: backend and mobile engineers joining the team), and the API reference from the OpenAPI file.

## What the agent produces

```
outputs/developer-guide/
  index.html               versions, newest first
  v1-2026-11-12.html       the guide
outputs/api/
  addons-v1.yaml           copied from the contract the code ships
```

Guide outline, each section citing its source path:

| Section | Source |
|---|---|
| Flow: list → order → authorise → activation → capture | `docs/requirements/v1-2026-11-02.html` AO-1..AO-3; ADR 0001 |
| Error codes and what the apps show | OpenAPI `components/schemas/Error`; app string files |
| Attempt cap and idempotency | `code/core-service/Payments/AuthoriseHandler.cs`; I-2 |
| Notifications | `code/notification-service/templates/addon_activated_*.json` |
| How to run locally | `CLAUDE.md` → Commands |

## Updating it later

A change after v1 is published goes into `v2-<date>.html` with a line in `index.html`; v1 stays. The `protect-published-versions` hook blocks edits to v1.

## Check before moving on

- Every statement cites a path; anything not in code or requirements is labelled an assumption.
- The reader is named at the top; the depth fits that reader.
