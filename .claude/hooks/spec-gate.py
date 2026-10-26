#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit): no code before an approved design.

An edit under code/ is allowed only when at least one spec in specs/ is in the
build phase or later with intent, spec and design approved. Projects with no
specs yet (setting up) are not gated. Set SPEC_GATE=off for an emergency fix
and say so in the commit message. Edits made through Bash are not seen here;
code review and `tools/spec.py check` cover those.
"""
import glob
import json
import os
import sys

GATED = ("code/",)
OPEN_PHASES = ("build", "test", "deploy", "maintain")


def main() -> None:
    if os.environ.get("SPEC_GATE", "").lower() == "off":
        return
    event = json.load(sys.stdin)
    path = (event.get("tool_input") or {}).get("file_path") or ""
    project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    rel = (os.path.relpath(path, project) if os.path.isabs(path) else path).replace(os.sep, "/")
    if not rel.startswith(GATED):
        return

    specs = [p for p in glob.glob(os.path.join(project, "specs", "*", "status.json"))
             if not os.path.basename(os.path.dirname(p)).startswith("_")]
    if not specs:
        return
    for p in specs:
        try:
            st = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ap = st.get("approved") or {}
        if st.get("phase") in OPEN_PHASES and all(ap.get(k) for k in ("intent", "spec", "design")):
            return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"{rel}: no spec is in the build phase with intent, spec and design approved. "
                "Run `python3 tools/spec.py list`, finish the open phase (/spec, /design), get it "
                "approved, then `tools/spec.py phase <KEY> build`. For a production fix use "
                "/fix-issue with SPEC_GATE=off and record it."
            ),
        }
    }))


if __name__ == "__main__":
    main()
