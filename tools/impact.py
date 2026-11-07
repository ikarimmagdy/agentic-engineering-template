#!/usr/bin/env python3
"""System impact: what each piece of work changes, merged into one system model.

  python3 tools/impact.py check [KEY]   validate specs/<KEY>-*/outputs/impact.json
  python3 tools/impact.py json          the merged system model (read by the Engineering Hub)
  python3 tools/impact.py show <id>     one component: what it talks to and every change to it

The model starts from repos.yaml (one component per repo, layer = its group) and
docs/architecture/baseline.json (layers, external systems, data stores, known flows), then
adds every spec's outputs/impact.json in date order. Each element keeps the list of
changes made to it, per spec. Schema: specs/README.md, "System impact".

Python 3.9+, standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spec import find, load, root, spec_dirs  # noqa: E402

CHANGES = ["added", "changed", "removed", "used"]
LAYERS = ["mobile", "edge", "core", "notification", "integrations", "platform", "external", "data"]
KINDS = ["app", "service", "gateway", "middleware", "database", "queue", "external", "platform"]
INFRA_KINDS = ["database", "table", "column", "stored-procedure", "config", "secret", "queue", "topic",
               "cache", "job", "k8s", "ingress", "certificate", "dns", "feature-flag", "other"]
LAYER_NAMES = {
    "mobile": "Mobile apps", "edge": "Edge and gateways", "core": "Core middleware",
    "notification": "Notification engine", "integrations": "Integration services",
    "platform": "Platform and delivery", "external": "External systems", "data": "Data stores",
}
GROUP_KIND = {"mobile": "app", "edge": "gateway", "core": "middleware", "platform": "platform"}
SECTIONS = ["components", "flows", "infra", "screens", "useCases"]


def repos(base: str) -> list[dict]:
    """repos.yaml without a YAML library: the `- name:` entries and their scalar fields."""
    path = os.path.join(base, "repos.yaml")
    out: list[dict] = []
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s*-\s+name:\s*(\S+)", line)
        if m:
            out.append({"name": m.group(1)})
            continue
        m = re.match(r"^\s+(group|stack|default|production):\s*(.+?)\s*$", line)
        if m and out:
            out[-1][m.group(1)] = m.group(2)
    return out


def baseline(base: str) -> dict:
    path = os.path.join(base, "docs", "architecture", "baseline.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def layer_ids(base: str) -> list[str]:
    """Layers a component may name: the baseline's, then the defaults and repos.yaml groups."""
    ids = [l["id"] for l in baseline(base).get("layers", [])]
    return ids + [x for x in LAYERS + [r.get("group", "") for r in repos(base)] if x and x not in ids]


def impact_file(d: str) -> str:
    return os.path.join(d, "outputs", "impact.json")


def read_impact(d: str) -> dict | None:
    p = impact_file(d)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def known_components(base: str) -> dict[str, dict]:
    comps: dict[str, dict] = {}
    for r in repos(base):
        g = r.get("group", "core")
        comps[r["name"]] = {"id": r["name"], "name": r["name"], "layer": g, "kind": GROUP_KIND.get(g, "service"),
                            "repo": r["name"], "stack": r.get("stack", ""), "summary": "", "baseline": True}
    for c in baseline(base).get("components", []):
        comps[c["id"]] = {**comps.get(c["id"], {}), **{k: v for k, v in c.items() if k != "aliases"}, "baseline": True}
    return comps


def validate(imp: dict, known: dict[str, dict], layers: list[str] | None = None) -> list[str]:
    errs = []
    layers = layers or LAYERS
    if imp.get("version") != 1:
        errs.append("version must be 1")
    for s in SECTIONS:
        if not isinstance(imp.get(s, []), list):
            errs.append(f"{s} must be a list")
    declared = {}
    for c in imp.get("components", []):
        cid = c.get("id")
        if not cid:
            errs.append("a component has no id")
            continue
        if cid not in known and not all(c.get(k) for k in ("name", "layer", "kind")):
            errs.append(f"component {cid}: not in repos.yaml or the baseline, so it needs name, layer and kind")
        if c.get("layer") and c["layer"] not in layers:
            errs.append(f"component {cid}: unknown layer '{c['layer']}' (use {', '.join(layers)})")
        if c.get("kind") and c["kind"] not in KINDS:
            errs.append(f"component {cid}: unknown kind '{c['kind']}'")
        declared[cid] = c
    for s in SECTIONS:
        for i, e in enumerate(imp.get(s, [])):
            if e.get("change") not in CHANGES:
                errs.append(f"{s}[{i}]: change must be one of {', '.join(CHANGES)}")
    for i, f in enumerate(imp.get("flows", [])):
        for end in ("from", "to"):
            if f.get(end) not in declared:
                errs.append(f"flows[{i}]: {end} '{f.get(end)}' is not in components")
    for i, x in enumerate(imp.get("infra", [])):
        if x.get("kind") not in INFRA_KINDS:
            errs.append(f"infra[{i}]: unknown kind '{x.get('kind')}'")
        if x.get("component") and x["component"] not in declared and x["component"] not in known:
            errs.append(f"infra[{i}]: component '{x['component']}' is unknown")
    for i, sc in enumerate(imp.get("screens", [])):
        if not sc.get("id") or not sc.get("name"):
            errs.append(f"screens[{i}]: needs id and name")
    return errs


def check_spec(d: str, base: str, known: dict | None = None) -> list[str]:
    """Problems with a spec's impact.json; spec.py check calls this from the build phase on."""
    try:
        imp = read_impact(d)
    except json.JSONDecodeError as e:
        return [f"outputs/impact.json is not valid JSON: {e}"]
    if imp is None:
        return ["outputs/impact.json is missing (what this work changes in the system; see specs/README.md)"]
    return validate(imp, known or known_components(base), layer_ids(base))


def flow_id(f: dict) -> str:
    return f"{f['from']}>{f['to']}:{f.get('interface') or f.get('protocol') or ''}"


def aliases(base: str) -> dict[str, str]:
    """Other ids specs used for a baseline component (`aliases` on its entry), mapped to its id."""
    return {a: c["id"] for c in baseline(base).get("components", []) for a in c.get("aliases", [])}


def canonical(imp: dict, alias: dict[str, str]) -> dict:
    if not alias:
        return imp
    to = lambda i: alias.get(i, i)  # noqa: E731
    imp = json.loads(json.dumps(imp))
    imp["components"] = list({to(c["id"]): {**c, "id": to(c["id"])} for c in imp.get("components", [])}.values())
    for f in imp.get("flows", []):
        f["from"], f["to"] = to(f["from"]), to(f["to"])
    for x in imp.get("infra", []):
        if x.get("component"):
            x["component"] = to(x["component"])
    for sc in imp.get("screens", []):
        if sc.get("app"):
            sc["app"] = to(sc["app"])
    for u in imp.get("useCases", []):
        u["components"] = [to(c) for c in u.get("components", [])]
    return imp


def model(base: str) -> dict:
    bl = baseline(base)
    comps = known_components(base)
    alias = aliases(base)
    order = [l["id"] for l in bl.get("layers", [])] or LAYERS
    layers = {l["id"]: l for l in bl.get("layers", [])}
    flows: dict[str, dict] = {}
    for f in bl.get("flows", []):
        flows[flow_id(f)] = {**f, "id": flow_id(f), "baseline": True, "changes": []}
    infra: dict[str, dict] = {}
    screens: dict[str, dict] = {}
    use_cases: list[dict] = []
    works: list[dict] = []
    for c in comps.values():
        c.setdefault("changes", [])

    specs = []
    for d in spec_dirs(base):
        imp = read_impact(d)
        if imp:
            imp = canonical(imp, alias)
            st = load(d)
            started = min((h.get("date", "") for h in st.get("history", []) if h.get("date")), default="") or imp.get("updated", "")
            specs.append((started, d, imp))
    # in the order the work started, so the model reads as the system growing
    for started, d, imp in sorted(specs, key=lambda x: x[0]):
        st = load(d)
        when = imp.get("updated") or st.get("updated") or started
        key, folder = st.get("key") or imp.get("key"), os.path.basename(d)

        def change(e: dict, extra: tuple = ()) -> dict:
            out = {"key": key, "change": e["change"], "summary": e.get("summary", ""), "date": when}
            for k in ("where",) + extra:
                if e.get(k):
                    out[k] = e[k]
            return out

        for c in imp.get("components", []):
            cur = comps.setdefault(c["id"], {"id": c["id"], "name": c.get("name", c["id"]), "layer": c.get("layer", "core"),
                                             "kind": c.get("kind", "service"), "repo": c.get("repo", ""), "stack": "",
                                             "summary": c.get("description", ""), "baseline": False, "changes": []})
            cur["changes"].append(change(c))
        for f in imp.get("flows", []):
            fid = flow_id(f)
            cur = flows.setdefault(fid, {"id": fid, "from": f["from"], "to": f["to"], "protocol": f.get("protocol", ""),
                                         "interface": f.get("interface", ""), "baseline": False, "changes": []})
            cur["changes"].append(change(f, ("reqs",)))
        for x in imp.get("infra", []):
            xid = x.get("id") or f"{x.get('component')}:{x['kind']}:{x.get('name')}"
            cur = infra.setdefault(xid, {"id": xid, "kind": x["kind"], "name": x.get("name", xid), "component": x.get("component", ""),
                                         "env": [], "changes": []})
            cur["env"] = sorted(set(cur["env"]) | set(x.get("env", [])))
            cur["changes"].append(change(x))
        for s in imp.get("screens", []):
            sid = f"{s.get('app', '')}:{s['id']}"
            cur = screens.setdefault(sid, {"id": sid, "name": s["name"], "app": s.get("app", ""), "platforms": [], "image": None, "changes": []})
            cur["platforms"] = sorted(set(cur["platforms"]) | set(s.get("platforms", [])))
            if s.get("image"):
                cur["image"] = f"specs/{folder}/{s['image']}"
            cur["changes"].append(change(s, ("reqs",)))
        for u in imp.get("useCases", []):
            use_cases.append({**u, "id": f"{key}:{u.get('id', len(use_cases))}", "key": key, "date": when})
        works.append({"key": key, "dir": folder, "title": st.get("title", ""), "phase": st.get("phase", ""), "started": started, "updated": when,
                      "summary": imp.get("summary", ""), "decisions": imp.get("decisions", []),
                      "counts": {s: len(imp.get(s, [])) for s in SECTIONS}})

    for c in comps.values():
        layers.setdefault(c["layer"], {"id": c["layer"]})
    for lid, l in layers.items():
        l.setdefault("name", LAYER_NAMES.get(lid, lid.title()))
    return {
        "version": 1,
        "generated": dt.date.today().isoformat(),
        "layers": sorted(layers.values(), key=lambda l: order.index(l["id"]) if l["id"] in order else len(order)),
        "components": sorted(comps.values(), key=lambda c: (c["layer"], c["name"].lower())),
        "flows": sorted(flows.values(), key=lambda f: f["id"]),
        "infra": sorted(infra.values(), key=lambda x: (x["kind"], x["name"])),
        "screens": sorted(screens.values(), key=lambda s: (s["app"], s["name"])),
        "useCases": use_cases,
        "works": works,
    }


def cmd_check(a) -> None:
    base = root()
    known = known_components(base)
    dirs = [find(base, a.key)] if a.key else spec_dirs(base)
    bad = 0
    for d in dirs:
        name = os.path.basename(d)
        if not os.path.exists(impact_file(d)):
            print(f"--   {name} (no impact.json)")
            continue
        errs = check_spec(d, base, known)
        if errs:
            bad += 1
            print(f"FAIL {name}\n  - " + "\n  - ".join(errs))
        else:
            imp = read_impact(d)
            print(f"ok   {name} (" + ", ".join(f"{len(imp.get(s, []))} {s}" for s in SECTIONS) + ")")
    sys.exit(1 if bad else 0)


def cmd_json(a) -> None:
    print(json.dumps(model(root()), indent=2, ensure_ascii=False))


def cmd_show(a) -> None:
    m = model(root())
    c = next((x for x in m["components"] if x["id"].lower() == a.id.lower()), None)
    if not c:
        sys.exit(f"no component {a.id}")
    print(f"{c['name']} ({c['layer']}, {c['kind']})")
    for f in m["flows"]:
        if c["id"] in (f["from"], f["to"]):
            print(f"  {f['from']} -> {f['to']}  {f['protocol']} {f['interface']}  [{', '.join(x['key'] for x in f['changes']) or 'baseline'}]")
    for ch in c["changes"]:
        print(f"  {ch['date']} {ch['key']} {ch['change']}: {ch['summary']}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("key", nargs="?"); c.set_defaults(fn=cmd_check)
    sub.add_parser("json").set_defaults(fn=cmd_json)
    s = sub.add_parser("show"); s.add_argument("id"); s.set_defaults(fn=cmd_show)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
