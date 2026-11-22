#!/usr/bin/env python3
"""SessionStart: orient the session — specs in flight, handoff state, latest requirements, last ADRs."""
from __future__ import annotations
import glob
import json
import os
import re
import subprocess
import sys

project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def latest_version(folder: str) -> str | None:
    files = glob.glob(os.path.join(project, folder, "v*-*"))
    key = lambda f: int(re.match(r"v(\d+)", os.path.basename(f)).group(1))
    files = [f for f in files if re.match(r"v\d+-", os.path.basename(f))]
    return os.path.relpath(max(files, key=key), project) if files else None


def last_adrs(n: int = 3) -> list[str]:
    files = sorted(glob.glob(os.path.join(project, "docs/adr/[0-9][0-9][0-9][0-9]-*.md")))
    files = [f for f in files if not os.path.basename(f).startswith("0000-")]
    return [os.path.basename(f) for f in files[-n:]]


def handoff_next() -> list[str]:
    path = os.path.join(project, "HANDOFF.md")
    if not os.path.exists(path):
        return []
    lines, grab = [], False
    for line in open(path, encoding="utf-8"):
        if line.startswith("## "):
            grab = line.strip().lower() in ("## next", "## blockers")
            continue
        if grab and line.strip():
            lines.append(line.rstrip())
    return lines[:8]


def specs_in_flight() -> list[str]:
    out = []
    for p in sorted(glob.glob(os.path.join(project, "specs", "*", "status.json"))):
        if os.path.basename(os.path.dirname(p)).startswith("_"):
            continue
        try:
            st = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if st.get("phase") != "done":
            out.append(f"{st.get('key')} {st.get('title')} — phase {st.get('phase')}")
    return out


def team_sync() -> list[str]:
    """Work items the team cannot see yet, and team work this clone does not have."""
    def git(*args, timeout=8):
        try:
            r = subprocess.run(["git", "-C", project, *args], capture_output=True, text=True, timeout=timeout)
            return r.stdout.strip() if r.returncode == 0 else None
        except Exception:
            return None
    if git("rev-parse", "--abbrev-ref", "@{u}") is None:
        return []
    git("fetch", "--quiet")
    out = []
    dirty = git("status", "--porcelain", "--", "specs/")
    if dirty:
        folders = sorted({l[3:].split("/")[1] for l in dirty.splitlines() if l[3:].startswith("specs/") and l[3:].count("/") >= 1})
        out.append("Work items with changes the team cannot see (spec.py shares them on the next approve, phase or task; "
                   "or commit and push): " + ", ".join(folders))
    ahead, behind = git("rev-list", "--count", "@{u}..HEAD"), git("rev-list", "--count", "HEAD..@{u}")
    if ahead and ahead != "0":
        out.append(f"{ahead} local commits not pushed: run `git pull --rebase && git push` so the team and the hub see them.")
    if behind and behind != "0":
        out.append(f"The team pushed {behind} commits you do not have: run `git pull --rebase` before starting work.")
    return out


def identity_warning() -> str:
    """The pre-commit hook only runs once core.hooksPath is set, so warn at session start too."""
    path = os.path.join(project, ".claude", "git-identity")
    if not os.path.exists(path):
        return ""
    expected = open(path, encoding="utf-8").readline().strip()
    if not expected or "{{" in expected:
        return ""
    r = subprocess.run(["git", "-C", project, "config", "user.email"], capture_output=True, text=True)
    actual = r.stdout.strip()
    ok = actual.endswith(expected) if expected.startswith("@") else actual == expected
    return "" if ok else (f"WARNING: git user.email is '{actual}', this project expects '{expected}'. "
                          "Fix it before committing (see .githooks/pre-commit).")


def main() -> None:
    json.load(sys.stdin)
    parts = []
    warning = identity_warning()
    if warning:
        parts.append(warning)
    sync = team_sync()
    if sync:
        parts.append("Team sync:\n" + "\n".join(f"- {s}" for s in sync))
    flight = specs_in_flight()
    if flight:
        parts.append("Specs in flight (/feature <KEY> for the next step):\n" + "\n".join(flight))
    req = latest_version("docs/requirements")
    if req:
        parts.append(f"Latest requirements: {req}")
    adrs = last_adrs()
    if adrs:
        parts.append("Latest ADRs: " + ", ".join(adrs))
    nxt = handoff_next()
    if nxt:
        parts.append("From HANDOFF.md (next / blockers):\n" + "\n".join(nxt))
    if parts:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n".join(parts),
            }
        }))


if __name__ == "__main__":
    main()
