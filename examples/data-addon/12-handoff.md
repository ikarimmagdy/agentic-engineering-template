# 12 — Handoff: `/handoff`

**Loop step:** leave the project so the next session (or the next engineer) can continue without asking. **Command:** `/handoff`. **Where:** `HANDOFF.md`; the `session-start` hook shows its "Next" section at the start of every session.

## What the engineer types

```
/handoff
```

## What Claude writes — `HANDOFF.md`

```markdown
# HANDOFF — Data add-ons

**Updated:** 2026-11-12

## Goal
Customers buy a data add-on in the app and use it within a minute (AO-1..AO-7).

## State
- Requirements v1 (AO-1..AO-7); ADR 0001 Accepted (payment rules in core).
- M1 done: core + gateway merged; double-charge fix merged (commit "reuse pending payment attempt").
- UAT deployed at https://uat.example.internal/addons — smoke 5/5 pass.
- Developer guide v1 in outputs/developer-guide/.

## Next
- M2: Android buy flow (AO-1, AO-2); map AO-ERR-* strings AR/EN.
- Measure AO-6 (60 s) p95 in UAT; register stays `partial` until measured.
- Amendment A-2026-11-10-1 (capture grace period) waiting for approver.

## Blockers
- Apple Pay sandbox merchant certificate not yet issued (owner: Payments).
```

## Check before moving on

- "Next" is concrete enough to start without reading the chat.
- Every open decision or approval is listed with its owner.
- The handoff is committed and pushed with the work.
