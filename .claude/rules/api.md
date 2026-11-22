---
paths:
  - "code/**/api/**"
  - "**/openapi*.{yaml,yml,json}"
---

# API rules

- The OpenAPI document is the contract; change it in the same commit as the code.
- Breaking changes need a new version or an ADR.
- Request and response models are explicit; never return internal objects as they are.
- Errors use one documented shape across the API.
