# Local environment

Everything needed to run, test and debug the project on a laptop, without touching a shared
environment.

| Tier | What | How |
|---|---|---|
| 0 Workstation | SDKs, CLIs, clients | `Brewfile` (or the platform's equivalent) + `bin/env doctor` |
| 1 Dependencies | Databases, cache, broker, identity, tracing | Docker Compose profile `deps` |
| 2 Mocks | Every external provider | Compose profile `mocks` (e.g. WireMock mappings per provider) |
| 3 Services | The project's own services | Compose profile `apps`, or run from the IDE against tiers 1–2 |
| 4 Production-like | Same manifests as the target cluster | local Kubernetes (`bin/env k8s up`) |

## Configuration

- `.env.example` lists every variable by name with a safe local default or `change-me`. It is
  tracked. `.env` is generated from it and never tracked.
- A secret never has a real value in either file; local secrets are generated, shared ones come
  from the secret store.
- Each spec's `plan.md` → Configuration names the variables it adds; add them here in the same
  pull request.

## Rules

- Ports bind to `127.0.0.1` only.
- No production personal data on a laptop; restores use masked or synthetic data.
- Anything that cannot run locally says why here and what to use instead.
