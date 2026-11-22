#!/usr/bin/env python3
"""PreToolUse (Bash, issue-tracker MCP): outward-facing actions ask the owner first.

- Every git push asks first; commits stay local and free. Catches forms a
  permission prefix rule misses: `git -C <dir> push`, `cd x && git push`,
  `git push` inside a script line.
- An issue-tracker MCP call (Jira, Linear) that transitions or changes a
  ticket's status asks first: moving a ticket's status is outward-facing.
Python 3.9 compatible.
"""
import json
import re
import sys

PUSH = re.compile(r"\bgit\b(\s+-[Cc]\s+\S+|\s+--?[\w-]+(=\S+)?)*\s+push\b")
TRACKER_TOOL = re.compile(r"^mcp__.*(jira|atlassian|linear)", re.IGNORECASE)
TRACKER_MOVE = re.compile(r"transition|status", re.IGNORECASE)
MOVE_KEYS = ("status", "state", "stateid", "transition", "transitionid", "transition_id")


def ask(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    tool = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return

    if tool == "Bash" and PUSH.search(tool_input.get("command") or ""):
        ask("A push is outward-facing and needs the owner's explicit approval.")
        return
    keys = {str(k).lower() for k in tool_input}
    if TRACKER_TOOL.search(tool) and (TRACKER_MOVE.search(tool) or keys.intersection(MOVE_KEYS)):
        ask("Moving a ticket's status is outward-facing; confirm with the owner first.")


if __name__ == "__main__":
    main()
