# 05 — Backlog

**Loop step:** turn requirements into ordered, checkable work. **Where:** `planning/BACKLOG.md`. Every task names the requirement IDs it serves.

## What the engineer types

> Plan the backlog for AO-1…AO-7 per service (app iOS, app Android, gateway, core, notification). Order by dependency. One line per task with the requirement IDs. Milestones: M1 core + gateway, M2 apps, M3 notifications and usage.

## What Claude produces — `planning/BACKLOG.md`

```markdown
# Backlog

## M1 — Core service and gateway
- [ ] core: `Order` + `PaymentAttempt` tables, migration with rollback (AO-3, AO-4, AO-7)
- [ ] core: POST /addons/orders — idempotent on order_id; one active add-on per size (AO-7)
- [ ] core: authorise via payment gateway; attempt counter, refuse 3rd with AO-ERR-ATTEMPTS (AO-2, AO-4)
- [ ] core: on billing activation event → capture; on failure → release authorisation (AO-3)
- [ ] gateway: routes /v1/addons, /v1/addons/orders; pass error codes through unchanged (AO-1, AO-4)
- [ ] contract: OpenAPI for the above, error codes listed (AO-1..AO-4)

## M2 — Apps
- [ ] iOS: add-on list + buy flow + Apple Pay (AO-1, AO-2)
- [ ] Android: add-on list + buy flow (AO-1, AO-2)
- [ ] both: map AO-ERR-ATTEMPTS and AO-ERR-ACTIVE to AR/EN strings (AO-4, AO-7)

## M3 — Notifications and usage
- [ ] core: emit `AddonActivated` event (AO-5)
- [ ] notification: templates AR/EN for push + SMS (AO-5)
- [ ] usage: refresh within 60 s, measure p95 in UAT (AO-6)
```

## Check before moving on

- Every requirement ID appears in at least one task; no task without an ID.
- Order follows dependencies (contract before apps).
- Tasks are small enough to review in one PR.
