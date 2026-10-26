# 03 — Decision: `/adr`

**Loop step:** record a choice between real alternatives before building it. **Command:** `/adr` (or the `adr-writer` agent). **Produces:** `docs/adr/NNNN-<slug>.md`, a row in `docs/adr/README.md`.

## When this is needed

AO-4 (max 2 attempts) and AO-3 (capture after activation) can be enforced in the mobile app, the API gateway or the core service. Picking one is a decision with consequences, so it gets an ADR.

## What the engineer types

```
/adr Where to enforce the payment attempt cap (AO-4) and the authorise/capture rule (AO-3): app, API gateway, or core service.
```

## What Claude produces

`docs/adr/0001-payment-rules-in-core-service.md`:

```markdown
# 0001 — Payment rules live in the core service

- **Status:** Proposed
- **Date:** 2026-11-03
- **Deciders:** Engineering lead, Payments owner
- **Supersedes / superseded by:** none

## Context
AO-3 and AO-4 control money. The app has two clients (iOS, Android) and the API gateway passes calls through.
A rule enforced in a client can be bypassed by an old app version or a direct API call.

## Options considered
1. **Mobile apps** — fast to show errors / two implementations, bypassable, old versions ignore it.
2. **API gateway (Ruby)** — one place / the gateway is stateless today and would need its own store for attempts.
3. **Core service (.NET)** — owns the order and payment records already; one implementation / errors must be mapped back through the gateway.

## Decision
Enforce AO-3 and AO-4 in the core service, against the order record. The gateway passes the error code through unchanged; the apps only display it.

## Consequences
- Easier: one source of truth, testable in one suite, no client can bypass it.
- Harder: the error code AO-ERR-ATTEMPTS must be documented in the API contract and localised in both apps.
- Ruled out: client-side counters as the control (they may exist for UX only).
```

`docs/adr/README.md` row: `| 0001 | Payment rules live in the core service | Proposed | 2026-11-03 |`.

## Acceptance

The owner reviews and says "accept 0001". Only then Claude changes the status line to **Accepted** and commits. After that the ADR is never rewritten; a later change is a new ADR that supersedes it.

## Check before moving on

- At least two options that were really possible, each with a cost.
- Consequences include the bad ones.
- The architecture rule it creates is added to `constitution/L2-architecture.md` with the ADR number (step 04).
