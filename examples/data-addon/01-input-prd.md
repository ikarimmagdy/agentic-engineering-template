# 01 — Input: the PRD arrives

**Loop step:** capture input. **Where:** `inputs/prd/`. **Rule:** inputs are never edited; everything derived from them cites them.

## What the engineer does

Save the product document as received:

```
inputs/prd/2026-11-02-data-addon.md
```

Then ask Claude:

> Read `inputs/prd/2026-11-02-data-addon.md`. List every requirement it states, every rule with a number in it, and every question it leaves open. Do not write requirements yet.

## The input (example PRD)

```markdown
# PRD — Buy a data add-on (self-care app)

Owner: Product · Date: 2026-11-02

## Goal
Customers on a monthly plan can buy an extra data add-on in the app and use it within a minute.

## Scope
- Add-ons: 5 GB / 7 days, 10 GB / 30 days, 25 GB / 30 days. Prices come from the catalogue.
- Pay with a saved card or a new card. Apple Pay on iOS.
- Payment is authorised first and captured only when the add-on is active.
- Max 2 payment attempts per order; after that the order is closed and the customer is told to try later.
- Push + SMS when the add-on is active. Arabic and English.
- Show the add-on in usage within 60 seconds.

## Out of scope
- Prepaid balance payment, gifting, auto-renew.

## Open questions
- What happens if billing activation fails after authorisation?
- Can a customer hold two active add-ons of the same size?
```

## What Claude returns (expected)

| Type | Item | Source line |
|---|---|---|
| Requirement | Buy one of three add-ons from the catalogue | Scope 1 |
| Requirement | Pay by saved / new card; Apple Pay on iOS | Scope 2 |
| Rule | Authorise first, capture on activation | Scope 3 |
| Rule | Max **2** payment attempts per order | Scope 4 |
| Requirement | Push + SMS on activation, AR and EN | Scope 5 |
| Rule | Visible in usage within **60 s** | Scope 6 |
| Open | Billing activation fails after authorisation → release the authorisation? | Open 1 |
| Open | Two active add-ons of the same size? | Open 2 |

## Check before moving on

- Every row cites a line of the PRD; nothing is invented.
- Open questions go to the product owner now, not after the code exists.
- The PRD file is unchanged (`git diff inputs/` is empty).
