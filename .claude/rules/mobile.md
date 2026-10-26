---
paths:
  - "**/*.swift"
  - "**/*.kt"
  - "**/*.kts"
  - "**/*.dart"
  - "tests/mobile/**"
---

# Mobile rules

- TLS certificate checks stay on in every build type; no trust-all managers or ATS exceptions outside a documented debug flag.
- No secrets, tokens or personal data in logs, crash reports or analytics.
- Every screen works in RTL and with the largest accessibility text size; controls have accessibility labels.
- Strings come from the localisation layer, never inline.
- Network calls go through the app's API client with timeouts and a defined error state on screen.
- New screens get component tests; new journeys get a mobile flow in `tests/mobile/`.
- Builds for a simulator use a debug configuration pointed at the local environment or a mock backend.
