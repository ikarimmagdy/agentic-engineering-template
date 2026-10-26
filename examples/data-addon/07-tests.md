# 07 — Tests: `test-writer`

**Loop step:** prove each requirement with tests named after it. **Agent:** `test-writer`. **Covers:** happy path, the edge cases the requirement names, one failure path.

## What the engineer types

> Use the test-writer agent for AO-3 and AO-4 in `code/core-service/`.

## What the agent produces

| Test | Requirement | Kind |
|---|---|---|
| `Authorise_FirstAttempt_Succeeds` | AO-2 | happy |
| `Authorise_ThirdAttempt_RefusedWithAttemptsCode` | AO-4 | edge (the number in the requirement) |
| `Authorise_SameIdempotencyKey_ChargesOnce` | I-2 | edge |
| `Activation_Confirmed_CapturesAuthorisation` | AO-3 | happy |
| `Activation_Failed_ReleasesAuthorisation` | AO-3 | failure |
| `Gateway_Timeout_RecordsFailedAttempt` | C-1 | failure |

Example (xUnit):

```csharp
[Fact] // AO-4
public async Task Authorise_ThirdAttempt_RefusedWithAttemptsCode()
{
    var order = Orders.WithFailedAttempts(2);
    var result = await _service.AuthoriseAsync(order.Id, Cards.Valid, default);
    Assert.Equal("AO-ERR-ATTEMPTS", result.Code);
    _gateway.VerifyNoOtherCalls();
}
```

Agent report: *Covered AO-2, AO-3, AO-4, I-2, C-1 (6 tests, all pass). Not covered: AO-6 (60 s usage) needs a UAT measurement, not a unit test.*

## Check before moving on

- Each test name or comment carries its requirement ID, so `/pr-review` can trace it.
- "Not covered" is stated, not hidden.
- Register status moves from `new` to `partial` or `built` through `/req` when a requirement is fully met.
