# 06 — Implementation

**Loop step:** build one backlog task. **Guards:** `constitution/`, the `.claude/rules/` file matching each path (loaded automatically by path), the `verify` skill before claiming it works.

## What the engineer types

> Implement the M1 task "core: authorise via payment gateway; attempt counter, refuse 3rd with AO-ERR-ATTEMPTS (AO-2, AO-4)" in `code/core-service/`. Follow ADR 0001 and I-2. Then run the verify skill.

## What Claude does

1. Reads `constitution/` and ADR 0001; the path `code/core-service/api/**` loads `.claude/rules/api.md` and `backend.md`, and the migration loads `database.md`.
2. Writes the smallest change that meets AO-2 and AO-4.
3. Runs the `verify` skill and reports a table.

Example of the core change (C#, abbreviated):

```csharp
public async Task<PaymentResult> AuthoriseAsync(Guid orderId, PaymentMethod method, CancellationToken ct)
{
    var order = await _orders.GetForUpdateAsync(orderId, ct);              // row lock: one attempt at a time
    if (order.PaymentAttempts.Count >= MaxAttempts)                         // AO-4, ADR 0001
        return PaymentResult.Refused("AO-ERR-ATTEMPTS");

    var attempt = order.NewAttempt(method);
    await _audit.WriteAsync("payment.authorise.start", orderId, ct);        // backend rule: audit first
    var result = await _gateway.AuthoriseAsync(
        idempotencyKey: $"{orderId}:{attempt.Number}",                      // I-2
        amount: order.Price, timeout: TimeSpan.FromSeconds(15), ct);       // C-1
    attempt.Record(result);
    await _orders.SaveAsync(order, ct);
    return result.IsAuthorised ? PaymentResult.Authorised(attempt.Id) : PaymentResult.Failed(result.Code);
}
```

Gateway route (Ruby, Grape) passes the code through unchanged:

```ruby
post 'addons/orders/:id/pay' do
  res = Core::Addons.pay(params[:id], declared(params)[:method], session_id: headers['Session-Id'])
  error!({ code: res.code, message: res.message }, 400) unless res.ok?  # C-2, ADR 0001
  present res.body
end
```

`verify` report:

| Step | Command | Result |
|---|---|---|
| build | `dotnet build code/core-service` | pass |
| lint | `dotnet format --verify-no-changes` | pass |
| test | `dotnet test code/core-service` | pass (42) |

## Check before moving on

- The commit message names the requirement IDs: `core: payment attempt cap (AO-2, AO-4)`.
- Every number in code (2 attempts, 15 s timeout) traces to a requirement or a standard.
- `verify` was actually run; never report a step that was not run.
