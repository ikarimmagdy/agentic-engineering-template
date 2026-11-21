#!/usr/bin/env python3
"""Check work items against the workspace rules the Engineering Hub relies on.

  python3 tools/hub_check.py [KEY ...] [--json]

For each work item in specs/ (or the keys given):
  diagrams   every phase the item has reached has outputs/diagrams/<phase>/v<N>-<date>.md (specs/README.md, "Diagrams")
  kinds      each diagram is a "## <Kind>: ..." section with one ```mermaid block; the kind places it in the hub
  index      every versioned folder (v<N>-<date>.* files) has a README.md or index.html listing its versions
  paths      no laptop path (/Users/..., C:\\Users, file:///) in the item's documents or outputs
  sections   a long document has sections: Markdown over 70 lines with at least three "## " headings, HTML over
             40 KB with at least three <h2>; otherwise the hub shows it as one long page
  design     from design on, plan.md records "Architecture choices" (the architect's decision table)
Errors exit 1; warnings do not. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASES = ["intent", "spec", "design", "build", "test", "deploy", "maintain"]
# the phase a diagram folder belongs to, and from which phase on it is expected (diagrams are written at the end of a phase)
DIAGRAM_DUE = {"intent": "spec", "spec": "design", "design": "build", "build": "test", "test": "deploy", "deploy": "maintain", "maintain": None}
KINDS = re.compile(r"^(containers?|context|components?|sequence|data model|deployment|pattern|states?|journey|requirement map|"
                   r"task|what changes|coverage|test path|deploy order|promotion|rollback|runbook|incident|idea)", re.I)
LOCAL = re.compile(r"(?<![\w.])(/Users/[A-Za-z]|[A-Z]:\\\\Users\\\\|file:///)")  # a laptop path; /home/app in a container is fine
VFILE = re.compile(r"^v\d+-\d{4}-\d{2}-\d{2}")


def check(d: Path) -> list[dict]:
    out = []
    add = lambda level, rule, where, text: out.append({"level": level, "rule": rule, "where": where, "text": text})  # noqa: E731
    try:
        st = json.loads((d / "status.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [{"level": "error", "rule": "status", "where": "status.json", "text": "status.json missing or unreadable"}]
    phase = st.get("phase", "intent")
    at = PHASES.index(phase) if phase in PHASES else 0
    rel = lambda p: p.relative_to(d).as_posix()  # noqa: E731

    for ph, due in DIAGRAM_DUE.items():
        if due and at >= PHASES.index(due) and not any((d / "outputs" / "diagrams" / ph).glob("v*-*.md")):
            add("warn", "diagrams", f"outputs/diagrams/{ph}/", f"no {ph} diagrams; the item is past {ph} (write them with the phase command's Diagrams step)")
    for f in sorted((d / "outputs" / "diagrams").glob("*/v*-*.md")):
        text = f.read_text(encoding="utf-8")
        parts = re.split(r"^## +", text, flags=re.M)[1:]
        if not parts:
            add("error", "kinds", rel(f), "no '## <diagram>' sections")
        for p in parts:
            title = p.split("\n", 1)[0].strip()
            if "```mermaid" not in p:
                add("error", "kinds", rel(f), f"'{title}' has no mermaid block")
            if not KINDS.match(title):
                add("warn", "kinds", rel(f), f"'{title}' does not start with a kind (Sequence:, Pattern:, States:, ...): the hub lists it under More diagrams")

    for folder in sorted({p.parent for p in d.rglob("*") if p.is_file() and VFILE.match(p.name)}):
        if not (folder / "README.md").exists() and not (folder / "index.html").exists():
            add("warn", "index", rel(folder) + "/", "versioned folder without README.md or index.html listing its versions")

    for f in sorted(p for p in d.rglob("*") if p.is_file() and p.suffix.lower() in (".md", ".html", ".htm", ".json", ".yaml", ".yml") and "inputs" not in p.relative_to(d).parts):
        text = f.read_text(encoding="utf-8", errors="ignore")
        m = LOCAL.search(text)
        if m:
            line = text[: m.start()].count("\n") + 1
            add("error", "paths", f"{rel(f)}:{line}", f"local path '{text[m.start():m.start() + 40].splitlines()[0]}': use a relative path or a name")
        if f.suffix.lower() == ".md" and "diagrams" not in f.parts and len(text.splitlines()) > 70:
            if len(re.findall(r"^## ", text, re.M)) < 3 and len(re.findall(r"^### ", text, re.M)) < 3:
                add("warn", "sections", rel(f), f"{len(text.splitlines())} lines with fewer than three '## ' sections: one long page in the hub")
        if f.suffix.lower() in (".html", ".htm") and len(text) > 40_000 and len(re.findall(r"<h2[\s>]", text, re.I)) < 3 and "floorplan" not in f.parts:
            add("warn", "sections", rel(f), f"{len(text) // 1024} KB with fewer than three <h2> sections: one long page in the hub")

    if at >= PHASES.index("build") and (d / "plan.md").exists() and not re.search(r"^#+ .*architecture choices", (d / "plan.md").read_text(encoding="utf-8"), re.I | re.M):
        add("warn", "design", "plan.md", "no 'Architecture choices' section (the architect's decision table: chosen, alternatives, why)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    dirs = sorted(p for p in (ROOT / "specs").iterdir() if p.is_dir() and (p / "status.json").exists())
    if a.keys:
        dirs = [p for p in dirs if any(p.name.startswith(f"{k}-") for k in a.keys)]
    report = {p.name: check(p) for p in dirs}
    errors = sum(1 for v in report.values() for x in v if x["level"] == "error")
    if a.json:
        print(json.dumps(report, indent=1))
    else:
        for name, items in report.items():
            if not items:
                print(f"ok    {name}")
                continue
            print(f"{'FAIL' if any(x['level'] == 'error' for x in items) else 'warn'}  {name}")
            for x in items:
                print(f"      {x['level']:5} {x['rule']:8} {x['where']}: {x['text']}")
        warns = sum(len(v) for v in report.values()) - errors
        print(f"\n{len(report)} work items: {errors} errors, {warns} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
