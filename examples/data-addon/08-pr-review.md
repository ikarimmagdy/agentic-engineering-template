# 08 — Review: `/pr-review`

**Loop step:** review the branch before merge. **Command:** `/pr-review` runs `code-reviewer`, and `security-auditor` when auth, data, secrets or integrations changed (payments do).

## What the engineer types

```
/pr-review
```

## What Claude returns (example)

**Requirement IDs in commits:** AO-2, AO-3, AO-4 — all present in `register.yaml`.

| # | Severity | Finding | Failing scenario | Smallest fix | Agent |
|---|---|---|---|---|---|
| 1 | High | `code/core-service/api/PaymentsController.cs:58` logs the full request body | card holder name and MSISDN reach the log store; breaks I-3 | log order ID and result code only | security-auditor |
| 2 | Medium | `code/core-service/Payments/AuthoriseHandler.cs:31` reads attempts without the row lock on the retry path | two taps within 50 ms both see 1 attempt and a 3rd authorisation goes through; breaks AO-4 | use `GetForUpdateAsync` on both paths | code-reviewer |
| 3 | Low | `code/gateway/app/api/v1/addons.rb:22` returns HTTP 500 for AO-ERR-ATTEMPTS | apps show a generic error instead of the localised message | map to 400 per C-2 | code-reviewer |

**Verdict:** don't merge. Fix 1 and 2, then re-run `/pr-review`.

## Check before moving on

- Every finding has file:line, a concrete failing scenario and a fix; vague findings are rejected.
- "No findings" is an acceptable answer; padding is not.
- Security findings block merge until fixed or explicitly accepted by the owner.
