---
paths:
  - "code/**/frontend/**"
  - "code/**/web/**"
  - "**/*.tsx"
---

# Frontend rules

- Accessible by default: keyboard reachable, labelled controls, visible focus, AA contrast.
- Support RTL when the product ships Arabic; use logical CSS properties, never hard-coded left/right.
- No secrets, privileged API keys or internal URLs in client code.
- No hard-coded user-visible strings where the app has a localisation layer.
- New user-visible behaviour is gated by a feature flag or remote config where the project has one.
- Copy and configuration live outside components where the project has a content layer.
