---
paths:
  - "**/test/**"
  - "**/tests/**"
  - "**/*Test*.*"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "specs/**/test-plan.md"
---

# Testing rules

Six layers. Prove each acceptance criterion at the lowest one that can.

| Layer | Proves | Runs against | Where |
|---|---|---|---|
| `unit` | One function or class | nothing outside the process | in the service repo |
| `component` | One UI component or screen renders and reacts | the UI framework's test runner, no backend | in the app repo |
| `functional` | One service end to end through its own API with real dependencies | containers (database, broker, identity, mocks) | in the service repo |
| `api` | The HTTP contract of a running service | the service in the local environment | `tests/api/` |
| `mobile` | A user journey in the app on a simulator or emulator | the local environment or a mock backend | `tests/mobile/` |
| `e2e` | The whole path across apps and services | the full local environment | `tests/e2e/` |

- Test names carry the acceptance criterion ID they prove.
- No test calls a real external provider or a shared environment. Use the mocks in `local-env/`.
- No sleeps; wait on a condition with a timeout.
- Test data is synthetic. Never production personal data.
- A bug fix starts with a failing test that reproduces it.
- A flaky test is a failing test: fix it or quarantine it with an issue link, never retry it silently.
- Every run that counts for a phase gate is saved under the spec's `outputs/test-runs/`.
