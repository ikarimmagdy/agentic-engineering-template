#!/usr/bin/env python3
"""Specs in flight: create, move through the loop, check, export.

  python3 tools/spec.py new <KEY> <slug> [--title "..."] [--intake KIND --ref R]
  python3 tools/spec.py intake <KEY> idea|jira|github-issue|pr [--ref R] [--summary S]
  python3 tools/spec.py list
  python3 tools/spec.py show <KEY>
  python3 tools/spec.py approve <KEY> intent|spec|design [--by NAME]
  python3 tools/spec.py phase <KEY> <phase> [--force]
  python3 tools/spec.py task <KEY> <task-id> todo|doing|review|done|blocked
  python3 tools/spec.py link <KEY> [--initiative K] [--epic K]... [--story K]... [--source URL]... [--repo R]...
  python3 tools/spec.py check [KEY]
  python3 tools/spec.py json

Outputs the json export also reads: outputs/review/<area>.md, outputs/findings.json,
outputs/feedback/v<N>-<date>.md (see specs/README.md).

Python 3.9+, standard library only. status.json is written only by this tool.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys

PHASES = ["intent", "spec", "design", "build", "test", "deploy", "maintain", "done"]
APPROVABLE = ["intent", "spec", "design"]
TASK_STATES = ["todo", "doing", "review", "done", "blocked"]
LAYERS = ["unit", "component", "functional", "api", "mobile", "e2e"]
TEST_STATES = ["planned", "written", "passing", "failing"]
APPROVAL_FILE = {"intent": "intent.md", "spec": "spec.md", "design": "plan.md"}
INTAKE_KINDS = ["idea", "jira", "github-issue", "pr"]
REVIEW_AREAS = ["scope", "architecture", "infra", "apis", "data", "localization", "ui-ux", "security", "tests"]
SEVERITIES = ["critical", "high", "medium", "low"]
LOOP_FILES = ["intent.md", "spec.md", "plan.md", "tasks.md", "test-plan.md"]

NEXT = {
    "intent": "/intent to finish intent.md, then the owner approves it",
    "spec": "/spec to write requirements and acceptance criteria (/gap for existing code)",
    "design": "/design for plan.md, data-model.md and contracts/",
    "build": "/tasks to break the design down, then /build <task-id>",
    "test": "/test to map every acceptance criterion to a passing test",
    "deploy": "/deploy <environment>",
    "maintain": "/maintain to watch it; /fix-issue for defects",
    "done": "nothing; the folder is the record",
}

REQ_ROW = re.compile(r"^\|\s*([A-Z][A-Z0-9_]*-\d+-R(\d+))\s*\|", re.M)
AC_DEF = re.compile(r"\*\*AC-R(\d+)\.(\d+)\*\*")
TEST_ROW = re.compile(r"^\|\s*(AC-R\d+\.\d+)\s*\|\s*([a-z-]+)\s*\|([^|]*)\|\s*([a-z]+)\s*\|\s*$", re.M)
TASK_ROW = re.compile(r"^(\|\s*(T\d+(?:\.\d+)?)\s*\|.*\|\s*)([a-z]+)(\s*\|\s*)$", re.M)
STATUS_LINE = re.compile(r"^\*\*Status:\*\*.*$", re.M)


def root() -> str:
    start = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, "specs", "_template")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            sys.exit("No specs/_template found above " + start)
        d = parent


def today() -> str:
    return dt.date.today().isoformat()


def spec_dirs(base: str) -> list[str]:
    out = []
    for d in sorted(glob.glob(os.path.join(base, "specs", "*"))):
        if os.path.isdir(d) and not os.path.basename(d).startswith("_") and os.path.exists(os.path.join(d, "status.json")):
            out.append(d)
    return out


def find(base: str, key: str) -> str:
    for d in spec_dirs(base):
        name = os.path.basename(d)
        if name == key or name.startswith(key + "-"):
            return d
    sys.exit(f"No spec folder for {key} under specs/")


def load(d: str) -> dict:
    with open(os.path.join(d, "status.json"), encoding="utf-8") as f:
        return json.load(f)


def save(d: str, st: dict) -> None:
    st["updated"] = today()
    with open(os.path.join(d, "status.json"), "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read(d: str, name: str) -> str:
    p = os.path.join(d, name)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def tasks(d: str) -> list[dict]:
    return [{"id": m.group(2), "status": m.group(3)} for m in TASK_ROW.finditer(read(d, "tasks.md"))]


def requirements(d: str) -> list[str]:
    return sorted({m.group(2) for m in REQ_ROW.finditer(read(d, "spec.md"))}, key=int)


def criteria(d: str) -> list[str]:
    return [f"AC-R{a}.{b}" for a, b in AC_DEF.findall(read(d, "spec.md"))]


def tests(d: str) -> list[dict]:
    return [{"ac": m.group(1), "layer": m.group(2), "test": m.group(3).strip(), "status": m.group(4)}
            for m in TEST_ROW.finditer(read(d, "test-plan.md"))]


def next_step(st: dict, tk: list[dict]) -> str:
    if st["phase"] == "build" and tk:
        open_tasks = [t["id"] for t in tk if t["status"] != "done"]
        return f"/build {st['key']} {open_tasks[0]}" if open_tasks else f"/test {st['key']}"
    return NEXT.get(st["phase"], "")


def summary(d: str) -> dict:
    st = load(d)
    tk = tasks(d)
    ts = tests(d)
    acs = criteria(d)
    covered = {t["ac"] for t in ts}
    passing = {t["ac"] for t in ts if t["status"] == "passing"}
    return {
        "key": st["key"], "title": st["title"], "folder": os.path.basename(d), "phase": st["phase"],
        "approved": st["approved"], "tracker": st.get("tracker", {}), "repos": st.get("repos", []),
        "updated": st.get("updated"), "next": next_step(st, tk),
        "requirements": len(requirements(d)), "criteria": len(acs),
        "criteria_tested": len([a for a in acs if a in covered]),
        "criteria_passing": len([a for a in acs if a in passing]),
        "tasks": {s: len([t for t in tk if t["status"] == s]) for s in TASK_STATES},
        "task_list": tk, "history": st.get("history", []),
        "dir": os.path.basename(d), "intake": st.get("intake"),
        "findings": findings_summary(d),
        "review": [a for a in REVIEW_AREAS if os.path.exists(os.path.join(d, "outputs", "review", a + ".md"))],
        "feedback": sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "outputs", "feedback", "v*.md"))),
        "files": [f for f in LOOP_FILES if written(d, f, st["key"], st["title"])],
    }


def template_text(name: str) -> str:
    return read(os.path.join(root(), "specs", "_template"), name)


def written(d: str, name: str, key: str, title: str) -> bool:
    """True when the file differs from the template (placeholders filled in)."""
    s = read(d, name)
    if not s.strip():
        return False
    t = template_text(name).replace("{{KEY}}", key).replace("{{TITLE}}", title)
    norm = lambda x: re.sub(r"\d{4}-\d{2}-\d{2}|\{\{DATE\}\}|\s+", "", x)
    return norm(s) != norm(t)


def findings_summary(d: str) -> dict | None:
    p = os.path.join(d, "outputs", "findings.json")
    if not os.path.exists(p):
        return None
    rows = json.load(open(p, encoding="utf-8")).get("findings", [])
    def count(field):
        out = {}
        for r in rows:
            k = r.get(field) or "none"
            out[k] = out.get(k, 0) + 1
        return out
    return {"total": len(rows), "bySeverity": count("severity"), "byDimension": count("dimension"),
            "byArea": count("area"), "open": len([r for r in rows if r.get("status", "open") == "open"])}


def problems(d: str, target: str | None = None) -> list[str]:
    """Return what blocks the spec from being in `target` (default: its current phase)."""
    st = load(d)
    phase = target or st["phase"]
    errs = []
    if phase not in PHASES:
        return [f"unknown phase '{phase}'"]
    at = PHASES.index(phase)
    ap = st.get("approved", {})
    for i, name in enumerate(APPROVABLE):
        if at > i and not ap.get(name):
            errs.append(f"{name} is not approved (needed from the {PHASES[i + 1]} phase on)")
    if at >= PHASES.index("design"):
        acs = criteria(d)
        for r in requirements(d):
            if not any(a.startswith(f"AC-R{r}.") for a in acs):
                errs.append(f"R{r} has no acceptance criteria in spec.md")
        if not requirements(d):
            errs.append("spec.md has no requirements")
    if at >= PHASES.index("build") and not tasks(d):
        errs.append("tasks.md has no tasks")
    if at >= PHASES.index("build"):
        from impact import check_spec
        errs += check_spec(d, root())
    ts = tests(d)
    for t in ts:
        if t["layer"] not in LAYERS:
            errs.append(f"{t['ac']}: unknown test layer '{t['layer']}' (use {', '.join(LAYERS)})")
        if t["status"] not in TEST_STATES:
            errs.append(f"{t['ac']}: unknown test status '{t['status']}'")
    if at >= PHASES.index("test"):
        open_tasks = [t["id"] for t in tasks(d) if t["status"] != "done"]
        if open_tasks:
            errs.append("tasks not done: " + ", ".join(open_tasks))
        covered = {t["ac"] for t in ts}
        missing = [a for a in criteria(d) if a not in covered]
        if missing:
            errs.append("acceptance criteria without a test in test-plan.md: " + ", ".join(missing))
    if at >= PHASES.index("deploy"):
        passing = {t["ac"] for t in ts if t["status"] == "passing"}
        notyet = [a for a in criteria(d) if a not in passing]
        if notyet:
            errs.append("acceptance criteria not passing: " + ", ".join(notyet))
    for t in tasks(d):
        if t["status"] not in TASK_STATES:
            errs.append(f"task {t['id']}: unknown status '{t['status']}'")
    return errs


def key_used(base: str, key: str) -> str:
    """Where KEY was used before, on this laptop or by anyone on the remote: a spec folder in
    specs/ now, in the history of any branch, or on an open pull request. Empty when free."""
    if any(os.path.basename(d).startswith(key + "-") for d in glob.glob(os.path.join(base, "specs", "*"))):
        return "a folder in specs/"
    def git(*args):
        r = subprocess.run(["git", "-C", base, *args], capture_output=True, text=True, timeout=60)
        return r.stdout if r.returncode == 0 else ""
    git("fetch", "--quiet", "origin", "+refs/heads/*:refs/remotes/origin/*", "+refs/pull/*/head:refs/remotes/origin/pr/*")
    for line in git("log", "--all", "--format=%h %an", "--name-only", "--diff-filter=A", "--", "specs/").splitlines():
        if line.startswith(f"specs/{key}-"):
            return f"{line.split('/')[1]} in the git history (git log --all -- specs/{key}-*)"
    return ""


def cmd_new(a) -> None:
    base = root()
    if not re.match(r"^[A-Z][A-Z0-9_]*-\d+$", a.key):
        sys.exit("KEY must look like PROJ-123")
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", a.slug):
        sys.exit("slug must be kebab-case")
    dest = os.path.join(base, "specs", f"{a.key}-{a.slug}")
    if os.path.exists(dest):
        sys.exit(f"{os.path.relpath(dest, base)} already exists")
    used = key_used(base, a.key)
    if used and not a.reuse_key:
        sys.exit(f"{a.key} is already used: {used}. Use the tracker key, or the next free key; "
                 "--reuse-key only if this is the same piece of work.")
    shutil.copytree(os.path.join(base, "specs", "_template"), dest)
    title = a.title or a.slug.replace("-", " ").capitalize()
    for p in glob.glob(os.path.join(dest, "**", "*"), recursive=True):
        if os.path.isfile(p) and p.endswith((".md", ".json")):
            s = open(p, encoding="utf-8").read()
            s = s.replace("{{KEY}}", a.key).replace("{{TITLE}}", title).replace("{{DATE}}", today())
            open(p, "w", encoding="utf-8").write(s)
    st = load(dest)
    st["history"].append({"date": today(), "event": "created"})
    if a.intake:
        st["intake"] = {"kind": a.intake, "ref": a.ref, "summary": a.summary}
        st["history"].append({"date": today(), "event": f"intake {a.intake}" + (f" {a.ref}" if a.ref else "")})
    save(dest, st)
    print(os.path.relpath(dest, base))


def cmd_list(a) -> None:
    rows = [summary(d) for d in spec_dirs(root())]
    if not rows:
        print("No specs yet. Start one: python3 tools/spec.py new <KEY> <slug>")
        return
    print(f"{'KEY':<14} {'PHASE':<9} {'TASKS':<7} {'AC TESTED':<10} TITLE")
    for r in rows:
        t = r["tasks"]
        done = f"{t['done']}/{sum(t.values())}"
        ac = f"{r['criteria_tested']}/{r['criteria']}"
        print(f"{r['key']:<14} {r['phase']:<9} {done:<7} {ac:<10} {r['title']}")


def cmd_show(a) -> None:
    d = find(root(), a.key)
    s = summary(d)
    print(json.dumps({k: v for k, v in s.items() if k != "task_list"}, indent=2, ensure_ascii=False))
    errs = problems(d)
    print("\nNext: " + s["next"])
    if errs:
        print("Blocking:\n- " + "\n- ".join(errs))


def cmd_approve(a) -> None:
    base = root()
    d = find(base, a.key)
    st = load(d)
    by = a.by or os.environ.get("USER", "owner")
    st["approved"][a.what] = {"date": today(), "by": by}
    st["history"].append({"date": today(), "event": f"approved {a.what}", "by": by})
    save(d, st)
    p = os.path.join(d, APPROVAL_FILE[a.what])
    s = open(p, encoding="utf-8").read()
    s = STATUS_LINE.sub(f"**Status:** approved {today()} by {by}", s, count=1)
    open(p, "w", encoding="utf-8").write(s)
    print(f"{a.key}: {a.what} approved by {by}")


def cmd_phase(a) -> None:
    d = find(root(), a.key)
    errs = problems(d, a.phase)
    if errs and not a.force:
        sys.exit(f"Cannot move {a.key} to {a.phase}:\n- " + "\n- ".join(errs))
    st = load(d)
    event = {"date": today(), "event": f"phase {st['phase']} -> {a.phase}"}
    if errs:
        event["forced"] = errs
    st["phase"] = a.phase
    st["history"].append(event)
    save(d, st)
    print(f"{a.key}: {a.phase}. Next: {next_step(st, tasks(d))}")


def cmd_task(a) -> None:
    d = find(root(), a.key)
    p = os.path.join(d, "tasks.md")
    s = open(p, encoding="utf-8").read()
    hit = [False]

    def repl(m):
        if m.group(2) != a.task:
            return m.group(0)
        hit[0] = True
        return m.group(1) + a.status + m.group(4)

    s = TASK_ROW.sub(repl, s)
    if not hit[0]:
        sys.exit(f"No task {a.task} in {os.path.relpath(p)}")
    open(p, "w", encoding="utf-8").write(s)
    st = load(d)
    st["history"].append({"date": today(), "event": f"task {a.task} -> {a.status}"})
    save(d, st)
    print(f"{a.key} {a.task}: {a.status}")


def cmd_link(a) -> None:
    d = find(root(), a.key)
    st = load(d)
    tr = st.setdefault("tracker", {"initiative": None, "epics": [], "stories": []})
    if a.initiative:
        tr["initiative"] = a.initiative
    for field, values in (("epics", a.epic), ("stories", a.story)):
        for v in values or []:
            if v not in tr[field]:
                tr[field].append(v)
    for field, values in (("sources", a.source), ("repos", a.repo)):
        for v in values or []:
            if v not in st.setdefault(field, []):
                st[field].append(v)
    save(d, st)
    print(json.dumps({"tracker": tr, "sources": st["sources"], "repos": st["repos"]}, indent=2))


def cmd_intake(a) -> None:
    d = find(root(), a.key)
    st = load(d)
    st["intake"] = {"kind": a.kind, "ref": a.ref, "summary": a.summary}
    st.setdefault("history", []).append({"date": today(), "event": f"intake {a.kind}" + (f" {a.ref}" if a.ref else "")})
    save(d, st)
    print(json.dumps(st["intake"], indent=2, ensure_ascii=False))


def cmd_check(a) -> None:
    base = root()
    dirs = [find(base, a.key)] if a.key else spec_dirs(base)
    bad = 0
    for d in dirs:
        errs = problems(d)
        name = os.path.basename(d)
        if errs:
            bad += 1
            print(f"FAIL {name}\n  - " + "\n  - ".join(errs))
        else:
            print(f"ok   {name} ({load(d)['phase']})")
    sys.exit(1 if bad else 0)


def cmd_json(a) -> None:
    print(json.dumps([summary(d) for d in spec_dirs(root())], indent=2, ensure_ascii=False))


SHARED = ("new", "intake", "link", "approve", "phase", "task")


def share(base: str, d: str) -> None:
    """Commit this work item's folder and push it, so the team (and the shared hub) sees it now."""
    mode = os.environ.get("SPEC_SHARE", "push").lower()
    if mode == "off":
        return
    def git(*args, timeout=120):
        return subprocess.run(["git", "-C", base, *args], capture_output=True, text=True, timeout=timeout)
    if git("rev-parse", "--is-inside-work-tree").returncode != 0:
        return
    rel = os.path.relpath(d, base)
    name = os.path.basename(d)
    key = load(d).get("key") or name
    event = (load(d).get("history") or [{}])[-1]
    msg = f"{key}: {event.get('event', 'updated')}" + (f", {event['by']}" if event.get("by") else "")
    git("add", "--", rel)
    staged = git("diff", "--cached", "--quiet", "--", rel).returncode != 0
    if staged:
        r = git("commit", "-q", "-m", msg, "--", rel)
        if r.returncode != 0:
            print(f"share: not committed ({(r.stderr or r.stdout).strip()[:300]}); commit {rel} yourself", file=sys.stderr)
            return
    if mode == "local":
        print(f"share: committed {rel} (SPEC_SHARE=local, not pushed)" if staged else "share: nothing new to commit", file=sys.stderr)
        return
    if git("remote").stdout.strip() == "":
        print("share: no git remote; committed locally", file=sys.stderr)
        return
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    if not staged and ahead.returncode == 0 and ahead.stdout.strip() == "0":
        return
    pull = git("pull", "--rebase", "--autostash", "-q")
    if pull.returncode != 0:
        git("rebase", "--abort")
        print("share: could not pull (conflict or offline); your commit is kept locally. "
              "Run `git pull --rebase` and `git push` when you can; the next spec.py command retries.", file=sys.stderr)
        return
    push = git("push", "-q", "origin", "HEAD") if git("rev-parse", "--abbrev-ref", "@{u}").returncode == 0 else git("push", "-q", "-u", "origin", "HEAD")
    if push.returncode != 0:
        print(f"share: push failed ({(push.stderr or '').strip()[:200]}); kept locally, the next spec.py command retries", file=sys.stderr)
        return
    print(f"share: {msg} pushed", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new"); n.add_argument("key"); n.add_argument("slug"); n.add_argument("--title"); n.add_argument("--reuse-key", action="store_true")
    n.add_argument("--intake", choices=INTAKE_KINDS); n.add_argument("--ref"); n.add_argument("--summary")
    n.set_defaults(fn=cmd_new)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    s = sub.add_parser("show"); s.add_argument("key"); s.set_defaults(fn=cmd_show)
    ap = sub.add_parser("approve"); ap.add_argument("key"); ap.add_argument("what", choices=APPROVABLE)
    ap.add_argument("--by"); ap.set_defaults(fn=cmd_approve)
    ph = sub.add_parser("phase"); ph.add_argument("key"); ph.add_argument("phase", choices=PHASES)
    ph.add_argument("--force", action="store_true"); ph.set_defaults(fn=cmd_phase)
    t = sub.add_parser("task"); t.add_argument("key"); t.add_argument("task"); t.add_argument("status", choices=TASK_STATES)
    t.set_defaults(fn=cmd_task)
    lk = sub.add_parser("link"); lk.add_argument("key"); lk.add_argument("--initiative")
    for flag in ("--epic", "--story", "--source", "--repo"):
        lk.add_argument(flag, action="append")
    lk.set_defaults(fn=cmd_link)
    ik = sub.add_parser("intake"); ik.add_argument("key"); ik.add_argument("kind", choices=INTAKE_KINDS)
    ik.add_argument("--ref"); ik.add_argument("--summary"); ik.set_defaults(fn=cmd_intake)
    c = sub.add_parser("check"); c.add_argument("key", nargs="?"); c.set_defaults(fn=cmd_check)
    sub.add_parser("json").set_defaults(fn=cmd_json)
    a = p.parse_args()
    a.fn(a)
    if a.cmd in SHARED:
        base = root()
        share(base, find(base, a.key))


if __name__ == "__main__":
    main()
