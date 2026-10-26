# 02 — Requirements: `/req`

**Loop step:** turn input into numbered, versioned requirements. **Command:** `/req` (runs the `requirements-keeper` agent). **Produces:** `docs/requirements/v1-<date>.html`, `register.yaml`, an index line, a change-log line.

## What the engineer types

```
/req Data add-on purchase from inputs/prd/2026-11-02-data-addon.md: catalogue of three add-ons, card and Apple Pay, authorise then capture on activation, max 2 payment attempts, push + SMS on activation in AR/EN, visible in usage within 60 s. Product answered: if activation fails the authorisation is released; only one active add-on per size.
```

The `prompt-router` hook would also remind Claude to use `/req` if you had written this as a plain message.

## What Claude produces

`docs/requirements/v1-2026-11-02.html` (excerpt of the body):

```html
<h2>AO — Data add-ons</h2>
<table>
<tr><th>ID</th><th>Requirement</th><th>Priority</th><th>Acceptance</th><th>Source</th></tr>
<tr><td>AO-1</td><td>The app lists add-ons from the catalogue with size, validity and price incl. VAT.</td><td>P0</td><td>List matches catalogue; price shows VAT.</td><td>PRD Scope 1</td></tr>
<tr><td>AO-2</td><td>The customer pays with a saved card, a new card, or Apple Pay (iOS).</td><td>P0</td><td>Each method completes an order in UAT.</td><td>PRD Scope 2</td></tr>
<tr><td>AO-3</td><td>Payment is authorised at order and captured only after billing confirms activation; if activation fails the authorisation is released.</td><td>P0</td><td>No capture without activation; failed activation shows a release in the gateway.</td><td>PRD Scope 3, Product 2026-11-02</td></tr>
<tr><td>AO-4</td><td>At most 2 payment attempts per order; the third is refused and the order closed.</td><td>P0</td><td>Third attempt returns error AO-ERR-ATTEMPTS.</td><td>PRD Scope 4</td></tr>
<tr><td>AO-5</td><td>Push and SMS on activation, Arabic and English.</td><td>P1</td><td>Both channels received in both languages.</td><td>PRD Scope 5</td></tr>
<tr><td>AO-6</td><td>The add-on shows in usage within 60 seconds of activation.</td><td>P1</td><td>p95 ≤ 60 s in UAT.</td><td>PRD Scope 6</td></tr>
<tr><td>AO-7</td><td>Only one active add-on of each size per line.</td><td>P1</td><td>Second purchase of an active size is refused.</td><td>Product 2026-11-02</td></tr>
</table>
```

`docs/requirements/register.yaml`:

```yaml
requirements:
  - { id: AO-1, title: Add-on catalogue in app,          priority: P0, status: new, since: v1 }
  - { id: AO-2, title: Card and Apple Pay payment,       priority: P0, status: new, since: v1 }
  - { id: AO-3, title: Authorise, capture on activation, priority: P0, status: new, since: v1 }
  - { id: AO-4, title: Max 2 payment attempts per order, priority: P0, status: new, since: v1 }
  - { id: AO-5, title: Activation push + SMS AR/EN,      priority: P1, status: new, since: v1 }
  - { id: AO-6, title: Usage visible within 60 s,        priority: P1, status: new, since: v1 }
  - { id: AO-7, title: One active add-on per size,       priority: P1, status: new, since: v1 }
```

`docs/requirements/index.html` gets a new first line: *v1 · 2026-11-02 · Data add-ons AO-1…AO-7 from the PRD and Product's answers.* `CLAUDE.md` change log gets one line. Commit: `requirements: v1 — data add-ons AO-1..AO-7`.

## Later change (shows versioning)

```
/req AO-4: Product changed the attempt cap from 2 to 3 per order.
```

Claude copies v1 to `v2-<date>.html`, changes AO-4 there (same ID), sets `since: v2` for AO-4 in the register, adds the index line. Editing v1 directly is blocked by the `protect-published-versions` hook.

## Check before moving on

- Every requirement has an ID, priority, acceptance and source.
- Answers from people are cited with name/role and date.
- Nothing in v1 contradicts `constitution/` or an accepted ADR; if it did, Claude must stop and say so.
