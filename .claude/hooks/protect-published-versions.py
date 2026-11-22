#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit): block edits to a published document version.

A versioned document is any file named v<N>-<YYYY-MM-DD>* anywhere in the
project (docs/, outputs/ or elsewhere). Once it is committed it has been seen,
so it is frozen: the change goes into the next version instead. Untracked
versions (still being drafted) and gitignored files stay editable. Tracking is
checked in the git repo that holds the file, so nested repos are covered too.
"""
import json
import os
import re
import subprocess
import sys
from typing import Optional

VERSIONED = re.compile(r"(^|/)v\d+-\d{4}-\d{2}-\d{2}[^/]*$")


def repo_root(folder: str) -> Optional[str]:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=folder, capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def is_tracked(rel: str, root: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", rel],
        cwd=root, capture_output=True, text=True,
    )
    return result.returncode == 0


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    path = (event.get("tool_input") or {}).get("file_path") or ""
    project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    if not path or not VERSIONED.search(path.replace(os.sep, "/")):
        return
    path = os.path.realpath(path if os.path.isabs(path) else os.path.join(project, path))
    if not os.path.exists(path):
        return
    root = repo_root(os.path.dirname(path))
    if not root:
        return
    rel = os.path.relpath(path, root)
    if not is_tracked(rel, root):
        return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"{rel} is a published version and is frozen. Copy it to the next "
                "v<N>-<date> file, edit the copy, and add a row to that folder's index."
            ),
        }
    }))


if __name__ == "__main__":
    main()
