#!/usr/bin/env python3
"""UserPromptSubmit: route a prompt to the project's process when it matches.

- A PRD, epic or new piece of work   -> /intent (then the loop in specs/).
- New or changed requirements        -> /spec for a feature, /req for product-wide ones.
- A decision being made              -> /adr.
- Build / test / deploy / a defect   -> /build, /test, /deploy, /fix-issue.

Matching is keyword-based on purpose: a hook cannot understand intent, so it
only reminds Claude which process applies. Claude still does the work.
"""
import json
import re
import sys

ROUTES = [
    (re.compile(r"\b(prd|epic|initiative|new feature|add (a )?feature|we need to (add|support|build))\b"
                r"|متطلب|ميزة جديدة", re.I),
     "New work detected. Start it in the loop: /intent <KEY> <slug> <source> creates specs/<KEY>-<slug>/ "
     "and its intent. Existing code involved: /gap <KEY>."),
    (re.compile(r"\b(requirements?|user stor(y|ies)|acceptance criteria|scope change)\b|متطلبات", re.I),
     "Requirements change detected. For a feature: /spec <KEY> (a change to an approved spec needs a "
     "Change log row and re-approval). For product-wide requirements: /req."),
    (re.compile(r"\b(we decided|i decided|decision is|let'?s (go with|use)|we will use|instead of|"
                r"switch(ing)? to|replace .+ with|trade-?off)\b", re.I),
     "A decision may be in this message. If it settles a choice with alternatives, draft an ADR with "
     "/adr (status Proposed) and ask the project owner to accept it."),
    (re.compile(r"\b(implement|build (it|the|this)|start coding|write the code)\b", re.I),
     "Building: run /feature <KEY> first. Code needs a spec in the build phase (the spec-gate hook "
     "enforces it); then /build <KEY> <task-id>."),
    (re.compile(r"\b(run (the )?tests?|e2e|end to end|simulator|emulator|regression)\b", re.I),
     "Testing: /test <KEY> [layer] runs the layers in order and records the run in the spec."),
    (re.compile(r"\b(deploy|release|promote|roll ?out)\b", re.I),
     "Deploying: /deploy <KEY> <environment>. Confirm the environment with the owner first."),
    (re.compile(r"\b(bug|defect|incident|broken|regression in|500 error|crash(es|ing)?)\b", re.I),
     "Defect: /fix-issue starts with a failing test that reproduces it."),
]


def main() -> None:
    prompt = (json.load(sys.stdin).get("prompt") or "")
    notes = [note for pattern, note in ROUTES if pattern.search(prompt)]
    if notes:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n".join(notes),
            }
        }))


if __name__ == "__main__":
    main()
