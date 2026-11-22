---
paths:
  - "code/**/backend/**"
  - "code/**/api/**"
  - "**/*.py"
---

# Backend rules

- Every entry point is authenticated and authorised; say why if one is public.
- Every write that matters is audited from the first line that performs it.
- Timeouts and retries on every outbound call; idempotency for anything that moves money or state.
- Validate input at the boundary; never trust model output as validated input.
- Responses from tools, integrations and model providers are size-capped before they reach a model.
- Inbound webhooks pass a signature check on every request and are idempotent by event id; public endpoints are rate-limited and audited.
- Secrets come only from the project's secret store or environment; never logged, never returned.
