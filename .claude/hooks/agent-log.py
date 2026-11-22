#!/usr/bin/env python3
"""PreToolUse and PostToolUse (Task|Agent): record each subagent run for the hub.

Appends one line per start and end to .claude/state/agent-runs.jsonl (gitignored): the
agent, its short description, the spec key it works on (a key from specs/ named in the
description or prompt), and the session. Never the prompt itself. The hub's local server
reads the file to show which agents are working on a work item and how they hand over.
Never blocks: any error is swallowed.
"""
import datetime as dt
import glob
import json
import os
import re
import sys


def keys(project: str) -> list:
    out = []
    for p in glob.glob(os.path.join(project, "specs", "*", "status.json")):
        try:
            k = json.load(open(p, encoding="utf-8")).get("key")
        except Exception:
            continue
        if k:
            out.append(k)
    return sorted(out, key=len, reverse=True)


def main() -> None:
    event = json.load(sys.stdin)
    if event.get("tool_name") not in ("Task", "Agent"):
        return
    project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    inp = event.get("tool_input") or {}
    text = f"{inp.get('description', '')}\n{str(inp.get('prompt', ''))[:4000]}"
    key = next((k for k in keys(project) if re.search(rf"\b{re.escape(k)}\b", text)), None)
    post = event.get("hook_event_name") == "PostToolUse"
    resp = event.get("tool_response")
    rec = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "event": "end" if post else "start",
        "id": event.get("tool_use_id"),
        "session": event.get("session_id"),
        "agent": inp.get("subagent_type") or "general-purpose",
        "description": str(inp.get("description", ""))[:200],
        "key": key,
        "source": "claude-code",
    }
    if post:
        rec["ok"] = not (isinstance(resp, dict) and resp.get("is_error"))
    state = os.path.join(project, ".claude", "state")
    os.makedirs(state, exist_ok=True)
    ignore = os.path.join(state, ".gitignore")
    if not os.path.exists(ignore):
        with open(ignore, "w", encoding="utf-8") as f:
            f.write("*\n")
    with open(os.path.join(state, "agent-runs.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
