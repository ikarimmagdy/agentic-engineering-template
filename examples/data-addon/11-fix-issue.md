# 11 — Fix a bug: `/fix-issue`

**Loop step:** reproduce, fix, test, review — in that order. **Command:** `/fix-issue`.

## What the engineer types

```
/fix-issue UAT: customer charged twice for one 10 GB add-on after the app timed out and the user tapped Pay again.
```

## What Claude does (example)

1. **Reproduce with a failing test:**

   ```csharp
   [Fact] // I-2, AO-3
   public async Task Authorise_RetryAfterClientTimeout_DoesNotChargeTwice() { … }
   ```

   It fails: two authorisations with different idempotency keys.
2. **Root cause (one sentence):** the retry after a client timeout created attempt 2 with key `order:2` while attempt 1 was still pending at the gateway, so the gateway saw two different payments.
3. **Smallest fix:** a pending attempt is reused instead of starting a new one; a new key is used only after the previous attempt has a final result.
4. **Tests:** the new test passes; full suite passes.
5. **Review:** `code-reviewer` on the diff → no findings.
6. **Commit:**

   ```
   core: reuse pending payment attempt on retry (I-2, AO-3)

   Root cause: a retry during a pending authorisation created a new idempotency key,
   so the gateway authorised twice.
   ```

## Check before moving on

- No fix without a failing test first, or a written reason why it cannot be reproduced.
- The root cause is in the commit message, not only in chat.
- If the bug shows a missing requirement or rule, run `/req` or `/amend` too.
