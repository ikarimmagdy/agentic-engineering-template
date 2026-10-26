# 09 — Deploy: `/deploy`

**Loop step:** ship to an environment the owner asked for, with a smoke test. **Command:** `/deploy <environment>`.

## What the engineer types

```
/deploy uat
```

## What Claude does and reports (example)

1. Confirms: *target UAT, requested by the engineering lead in this session.*
2. Builds and runs the full test suite: 128 passed, 0 failed.
3. Checks consistency: requirements v1 and ADR 0001 (Accepted) match what ships; AO-6 still `partial`.
4. Runs the deploy command from `CLAUDE.md` → Commands.
5. Smoke test:

| Check | Result |
|---|---|
| GET /v1/addons returns 3 add-ons with VAT prices | pass |
| Order + authorise with sandbox card | pass |
| Third attempt returns AO-ERR-ATTEMPTS (400) | pass |
| Activation event → capture visible in gateway sandbox | pass |
| Push + SMS received AR/EN | pass (SMS via simulator) |

Report: *UAT deployed at `https://uat.example.internal/addons`, smoke 5/5 pass. AO-6 timing still to measure.*

## Check before moving on

- No deploy without an explicit request; production needs its own request.
- A failed test stops the deploy; Claude does not "deploy anyway".
- The URL and the smoke results go into `HANDOFF.md` (step 12).
