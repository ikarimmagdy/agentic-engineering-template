#!/usr/bin/env python3
"""Findings: classify and summarise a spec's outputs/findings.json.

  python3 tools/findings.py classify <KEY> [--force]   set type, component and team on every finding
  python3 tools/findings.py summary <KEY>               counts by type, component, team and severity

Three questions a finding answers, kept apart from severity:
  type       what kind of problem   App / functional, UI/UX, Security, SRE / reliability,
                                    Technical debt, Localization, Gap
  component  where it lives         from tools/findings-map.json (layers, services, fileHints)
  team       who owns the fix       from tools/findings-map.json (teams, defaultTeam)

tools/findings-map.json is the project's own map; without it a finding's component is its layer.
  {"layers": {"ios": "iOS app"}, "appLayers": ["app"], "services": [["promissory", "promissory-service"]],
   "fileHints": [["nafith", "promissory-service"]], "teams": {"iOS app": "Mobile"}, "defaultTeam": "Unknown"}

Rules are below and deterministic. A value already set is kept unless --force; set one by hand when a rule is wrong.
Run after /gap, /pr-review and /feedback. Standard library only.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_FILE = os.path.join(ROOT, "tools", "findings-map.json")
MAP = json.load(open(MAP_FILE, encoding="utf-8")) if os.path.exists(MAP_FILE) else {}

LAYER_COMPONENT = MAP.get("layers", {})
APP_LAYERS = MAP.get("appLayers", [])
SERVICES = [tuple(x) for x in MAP.get("services", [])]
FILE_HINTS = [tuple(x) for x in MAP.get("fileHints", [])]
TEAM = MAP.get("teams", {})
DEFAULT_TEAM = MAP.get("defaultTeam", "Unknown")


def component(f: dict) -> str:
    layer = (f.get("layer") or "").lower()
    if layer in APP_LAYERS:
        text = f"{f.get('location', '')} {f.get('title', '')}"
        ios, android = bool(re.search(r"\bios\b|\.swift", text, re.I)), bool(re.search(r"android|\.kt\b|\.java\b", text, re.I))
        return "iOS app" if ios and not android else "Android app" if android and not ios else "iOS + Android"
    if layer in LAYER_COMPONENT:
        return LAYER_COMPONENT[layer]
    loc = (f.get("location") or "").lower().lstrip("`")
    # 0. several clauses, each starting with a different service: the finding spans services
    starts = {name for clause in re.split(r"[;,]\s*", loc) for pat, name in SERVICES if re.match(r"`?(?:" + pat + r")", clause)}
    if len(starts) > 1:
        return "Integration services"
    # 1. the service named at the start of the location owns the finding
    for pat, name in SERVICES:
        if re.match(r"(?:" + pat + r")", loc):
            return name
    # 2. a class or file only one service has
    for pat, name in FILE_HINTS:
        if re.search(pat, loc) and not any(re.search(p2, loc) for p2, n2 in FILE_HINTS if n2 != name):
            return name
    text = f"{f.get('location', '')} {f.get('title', '')}".lower()
    hits = sorted({name for pat, name in SERVICES if re.search(pat, text)},
                  key=lambda n: min((m.start() for pat, nm in SERVICES if nm == n for m in re.finditer(pat, text)), default=0))
    if len(hits) == 1:
        return hits[0]
    return "Integration services" if hits or layer == "integrations" else (layer or "Unknown")


def ftype(f: dict) -> str:
    dim, area = (f.get("dimension") or "").lower(), (f.get("area") or "").lower()
    cat = (f.get("category") or "").lower()
    if area == "localization" or "arabic" in cat or "locali" in cat:
        return "Localization"
    if dim == "security" or area == "security":
        return "Security"
    if dim in ("reliability", "performance", "release") or area == "infra":
        return "SRE / reliability"
    if dim == "maintainability" or area == "tests":
        return "Technical debt"
    if dim == "functional":
        return "UI/UX" if area == "ui-ux" else "App / functional"
    if (f.get("kind") or "") == "gap":
        return "Gap"
    return "Not set"


def find(key: str) -> str:
    hits = [d for d in glob.glob(os.path.join(ROOT, "specs", f"{key}-*")) if os.path.isdir(d)]
    if not hits:
        sys.exit(f"No spec folder for {key}")
    return os.path.join(hits[0], "outputs", "findings.json")


def cmd_classify(a) -> None:
    p = find(a.key)
    data = json.load(open(p, encoding="utf-8"))
    changed = 0
    for f in data.get("findings", []):
        for field, fn in (("component", component), ("type", ftype)):
            if a.force or not f.get(field):
                v = fn(f)
                changed += f.get(field) != v
                f[field] = v
        team = TEAM.get(f["component"], "Unknown" if f["component"] == "Unknown" else DEFAULT_TEAM)
        if a.force or not f.get("team"):
            changed += f.get("team") != team
            f["team"] = team
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"{os.path.relpath(p, ROOT)}: {len(data.get('findings', []))} findings, {changed} values set")
    cmd_summary(a)


def cmd_summary(a) -> None:
    rows = json.load(open(find(a.key), encoding="utf-8")).get("findings", [])
    for field in ("type", "component", "team", "severity"):
        c = collections.Counter(r.get(field) or "Not set" for r in rows)
        print(f"\n{field}:\n" + "\n".join(f"  {n:>4}  {k}" for k, n in c.most_common()))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classify"); c.add_argument("key"); c.add_argument("--force", action="store_true"); c.set_defaults(fn=cmd_classify)
    s = sub.add_parser("summary"); s.add_argument("key"); s.set_defaults(fn=cmd_summary)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
