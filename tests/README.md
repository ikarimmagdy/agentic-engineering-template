# Cross-service tests

Unit, component and functional tests live in each service or app repo. The layers that span
services live here (see `.claude/rules/testing.md`):

| Folder | Layer | Runs against |
|---|---|---|
| `api/` | HTTP contract tests per service | services running in `local-env/` |
| `mobile/` | App journeys on a simulator or emulator | local environment or mock backend |
| `e2e/` | Whole paths across apps and services | the full local environment |

Every test names the acceptance criterion it proves (`AC-R1.1`), and every run that counts for a
spec's gate is saved in that spec's `outputs/test-runs/`.
