# Test plan — {{KEY}} {{TITLE}}

Every acceptance criterion in [spec.md](spec.md) appears here at least once, at the lowest
layer that can prove it. `tools/spec.py check` fails when one is missing.

| AC | Layer | Test | Status |
|---|---|---|---|
| AC-R1.1 | {{unit}} | {{repo/path/to/TestFile::test_name_AC_R1_1}} | planned |

**Layers** (see `.claude/rules/testing.md`): `unit` · `component` (UI components) ·
`functional` (one service with its real dependencies in containers) · `api` (HTTP contract
against a running service) · `mobile` (app on a simulator or emulator) · `e2e` (the whole path
across services and apps).

**Status:** planned → written → passing (or `failing` with a link to the run).

## Environments
| Layer | Where it runs | Dependencies |
|---|---|---|

## Test data
{{Accounts, numbers, cards, documents used; where they come from; never real personal data.}}

## Results
Runs are saved in `outputs/test-runs/<date>-<layer>.md` with the command, the result and the commit.
