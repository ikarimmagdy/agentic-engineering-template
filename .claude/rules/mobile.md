---
paths:
  - "**/*.swift"
  - "**/*.kt"
  - "**/*.kts"
  - "**/*.dart"
  - "tests/mobile/**"
---

# Mobile rules

- TLS certificate checks stay on in every build type; no trust-all managers or ATS exceptions outside a documented debug flag. Certificate pinning stays on where it is present; never disable it to make a build or test pass.
- No secrets, tokens, card data or personal data in logs, crash reports or analytics. Strip or guard debug logging in release builds.
- Secrets come from the build/config layer (Gradle properties, xcconfig, `--dart-define`, CI), never from source. No keystores, service-account JSON, `local.properties` or `.env*` in git.
- Never trust a client-side amount, ID or role; the server decides.
- A new dependency needs a licence check, last release date and open CVEs before it is added.
- Every screen works in RTL (start/end, leading/trailing, never left/right) and with the largest accessibility text size; controls have accessibility labels.
- Strings come from the localisation layer, never inline; add every shipped language together.
- Network calls go through the app's API client with timeouts and a defined error state on screen.
- Unhappy paths are handled: nulls, empty lists, error branches, cancellation. Errors are not swallowed; a bare `catch {}` needs a comment justifying it.
- Lifecycle: listeners unregistered, observers and streams closed on teardown (Activity/Fragment, view controllers, Flutter `dispose`).
- Concurrency: UI work on the main thread only, no races on init, no unguarded shared mutable state.
- New user-visible behaviour is gated by a feature flag or remote config where the app has one.
- No `build/`, `Pods/` or other generated artifacts committed.
- New screens get component tests; new journeys get a mobile flow in `tests/mobile/`.
- Builds for a simulator use a debug configuration pointed at the local environment or a mock backend.
