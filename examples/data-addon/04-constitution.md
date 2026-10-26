# 04 — Constitution and `/amend`

**Loop step:** keep the few rules that must always hold in `constitution/`, and change them only on purpose. **Command:** `/amend`. **Produces:** rows in `L1`–`L3`, an entry in `AMENDMENTS.md`.

## The constitution for this example

`constitution/L1-invariants.md`:

| ID | Invariant | Why |
|---|---|---|
| I-1 | Money moves only after the state change it pays for is confirmed (capture after activation). | Customers are never charged for a service they did not get. |
| I-2 | Every payment call is idempotent on the order ID. | Retries and double taps never charge twice. |
| I-3 | No personal data (MSISDN, card, national ID) in logs or analytics events. | Privacy and regulation. |

`constitution/L2-architecture.md`:

| ID | Rule | ADR |
|---|---|---|
| A-1 | Payment and order rules are enforced in the core service; gateway and apps pass codes through. | 0001 |
| A-2 | Notifications are sent by the notification service from an event; no service sends SMS directly. | 0002 (example) |

`constitution/L3-code-standards.md`:

| ID | Standard |
|---|---|
| C-1 | Every outbound call has a timeout and a bounded retry. |
| C-2 | Error responses use one shape: `{ "code": "AO-ERR-…", "message": "…" }`. |
| C-3 | User-facing text comes from string files (AR/EN), never hard-coded. |

## Changing a rule: `/amend`

Product asks for a 2-minute grace period where a payment can be captured before activation is confirmed, to fix slow billing. That breaks I-1, so it is an amendment, not a code change.

```
/amend I-1: allow capture before activation confirmation if billing has not answered within 120 s, with automatic refund if activation then fails.
```

Claude adds to `constitution/AMENDMENTS.md`:

```
## A-2026-11-10-1 — I-1
Article:  I-1 Money moves only after the state change it pays for is confirmed
Change:   Capture allowed after 120 s without a billing answer; automatic refund if activation then fails
Why:      Billing confirmation p95 is 140 s; customers abandon while waiting
Cost:     Refund handling and reconciliation; a window where money moved without service
Approver: (pending)
```

and updates the I-1 text with `(amended A-2026-11-10-1)`. **It does not commit** until the approver is filled in.

## Check before moving on

- Invariants are few and testable; anything negotiable belongs in L2/L3 or requirements.
- Every L2 rule names its ADR.
- An amendment states the cost accepted, not just the change.
