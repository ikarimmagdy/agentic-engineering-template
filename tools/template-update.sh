#!/usr/bin/env bash
# ============================================================
# Update this workspace's agentic setup to the latest template.
#
#   tools/template-update.sh [--dry-run] [--adopt] [--ref <branch|tag>] [workspace-dir]
#
# Source: TEMPLATE_DIR (a local checkout inside git) or a full clone of
# AGENTIC_TEMPLATE_REPO (default the private template repo) at --ref (main).
# TEMPLATE_HISTORY: more template checkouts (colon-separated, each inside git) whose
# history also counts when recognising an untouched older template copy.
# Only the paths in the template's tools/template-files.txt are template-owned.
# Everything else belongs to the workspace and is never read or written.
#
# For each template-owned file:
#   same as the template                   nothing
#   an untouched older template copy       replaced
#   edited here since the recorded version three-way merged; kept as it is on conflict
#   edited here, no recorded version       kept and listed for review
#   missing here                           added in "full" mode only
# hub/: when the workspace has hub/content/brand.json, its engine files are updated from the
# template's hub/ with hub-update.sh (content/ is never touched); --adopt adds a starter hub/.
# Files the workspace added itself are never touched or removed. Never commits.
#
# Modes, recorded in .template-version with the version, template commit and date:
#   full      the workspace carries the whole template (--adopt sets it)
#   existing  only the template files it already has are kept up to date (default)
# ============================================================
set -euo pipefail

REPO="${AGENTIC_TEMPLATE_REPO:-https://github.com/ikarimmagdy/agentic-engineering-template.git}"
REF="main"; DRY=0; ADOPT=0; WS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --ref) REF="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --adopt) ADOPT=1; shift ;;
    -h|--help) sed -n '2,23p' "$0"; exit 0 ;;
    *) WS="$1"; shift ;;
  esac
done
WS="$(cd "${WS:-.}" && pwd)"
[ -d "$WS/.claude" ] || { echo "Not an agentic workspace (no .claude/): $WS" >&2; exit 1; }

TMP=""
cleanup() { [ -z "$TMP" ] || rm -rf "$TMP"; }
trap cleanup EXIT
if [ -n "${TEMPLATE_DIR:-}" ]; then
  SRC="$(cd "$TEMPLATE_DIR" && pwd)"
else
  TMP="$(mktemp -d)"; SRC="$TMP/tpl"
  git clone -q --branch "$REF" "$REPO" "$SRC"
fi
[ -f "$SRC/tools/template-files.txt" ] || { echo "Template has no tools/template-files.txt: $SRC" >&2; exit 1; }
[ "$SRC" != "$WS" ] || { echo "Refusing to update the template from itself" >&2; exit 1; }

VER="$(cat "$SRC/VERSION" 2>/dev/null || echo unknown)"
SHA="$(git -C "$SRC" log -1 --format=%h -- . 2>/dev/null || echo local)"
STAMP="$WS/.template-version"
OLD_VER=""; MODE="existing"
if [ -f "$STAMP" ]; then
  OLD_VER="$(awk '{print $1}' "$STAMP")"
  MODE="$(awk '{print $4}' "$STAMP")"; MODE="${MODE:-existing}"
fi
[ "$ADOPT" = 1 ] && MODE="full"
echo "==> $WS: template ${OLD_VER:-unrecorded} -> $VER ($SHA), mode $MODE"

# the template commit whose VERSION was the workspace's recorded version: the base for three-way merges
BASE=""
if [ -n "$OLD_VER" ]; then
  for c in $(git -C "$SRC" log --format=%H -- VERSION 2>/dev/null); do
    if [ "$(git -C "$SRC" show "$c:./VERSION" 2>/dev/null | tr -d '[:space:]')" = "$OLD_VER" ]; then BASE="$c"; break; fi
  done
fi

list_files() {
  grep -v '^\s*#' "$SRC/tools/template-files.txt" | sed '/^\s*$/d' | while read -r p; do
    case "$p" in
      */) [ -d "$SRC/$p" ] && (cd "$SRC" && find "${p%/}" -type f ! -name '.DS_Store' ! -path '*/__pycache__/*' | sort) ;;
      *) [ -f "$SRC/$p" ] && echo "$p" ;;
    esac
  done
}

# every version every template file has had, as "<path> <blob>", from the source and TEMPLATE_HISTORY
HIST="$(mktemp)"
for d in "$SRC" $(echo "${TEMPLATE_HISTORY:-}" | tr ':' ' '); do
  [ -d "$d" ] || continue
  for c in $(git -C "$d" log --format=%H -- . 2>/dev/null); do
    git -C "$d" ls-tree -r "$c" -- . 2>/dev/null | awk '{print $4, $3}'
  done
done | sort -u > "$HIST"
cleanup() { rm -f "$HIST"; [ -z "$TMP" ] || rm -rf "$TMP"; }

# true when the workspace file is byte-identical to some earlier version of the template file
is_old_template() {
  grep -qxF "$1 $(git hash-object "$WS/$1")" "$HIST"
}

n_same=0; n_local=0; n_add=0; n_upd=0; n_merge=0; n_kept=0; n_skip=0
KEPT=""
while read -r f; do
  [ -n "$f" ] || continue
  if [ ! -e "$WS/$f" ]; then
    if [ "$MODE" = full ]; then
      echo "  add      $f"; n_add=$((n_add+1))
      [ "$DRY" = 1 ] || { mkdir -p "$WS/$(dirname "$f")"; cp -p "$SRC/$f" "$WS/$f"; }
    else
      n_skip=$((n_skip+1))
    fi
  elif cmp -s "$SRC/$f" "$WS/$f"; then
    n_same=$((n_same+1))
  elif is_old_template "$f"; then
    echo "  update   $f"; n_upd=$((n_upd+1))
    [ "$DRY" = 1 ] || cp -p "$SRC/$f" "$WS/$f"
  elif [ -n "$BASE" ] && git -C "$SRC" cat-file -e "$BASE:./$f" 2>/dev/null; then
    t="$(mktemp)"; b="$(mktemp)"
    cp "$WS/$f" "$t"; git -C "$SRC" show "$BASE:./$f" > "$b"
    if cmp -s "$b" "$SRC/$f"; then
      n_local=$((n_local+1))   # the template has not changed this file since the recorded version
    elif git merge-file -q "$t" "$b" "$SRC/$f" 2>/dev/null; then
      echo "  merge    $f"; n_merge=$((n_merge+1))
      [ "$DRY" = 1 ] || cat "$t" > "$WS/$f"
    else
      echo "  KEPT     $f (local edits conflict with the template)"; n_kept=$((n_kept+1)); KEPT="$KEPT $f"
    fi
    rm -f "$t" "$b"
  else
    echo "  KEPT     $f (edited here)"; n_kept=$((n_kept+1)); KEPT="$KEPT $f"
  fi
done <<EOF
$(list_files)
EOF

echo "==> $n_upd updated, $n_merge merged, $n_add added, $n_same already current, $n_local local edits on files the template has not changed, $n_kept kept with local edits$( [ "$n_skip" -gt 0 ] && echo ", $n_skip template files not used here (mode existing)")"
if [ -n "$KEPT" ]; then
  echo "    compare a kept file with:  diff <workspace>/<file> <template>/<file>"
fi
# the hub: the template's hub/ carries the engine; a workspace's hub/ keeps its content/, only the engine moves
if [ -f "$SRC/hub/tools/engine-files.txt" ]; then
  if [ -f "$WS/hub/content/brand.json" ]; then
    HUB_TEMPLATE_DIR="$SRC/hub" bash "$SRC/hub/tools/hub-update.sh" $([ "$DRY" = 1 ] && echo --dry-run) "$WS/hub" 2>&1 \
      | grep -E '^==> hub|^  (add|update|retire)|rror' | sed 's/^/  hub: /' || true
  elif [ "$ADOPT" = 1 ]; then
    echo "  add      hub/ (starter hub: fill hub/content/brand.json, then cd hub && node build.mjs)"
    [ "$DRY" = 1 ] || { cp -R "$SRC/hub" "$WS/hub"; rm -rf "$WS/hub/content/kb-src" "$WS/hub/content/learning-src" "$WS/hub/content/manifest.json"; }
  fi
fi
if [ "$DRY" = 1 ]; then echo "==> dry run: nothing changed"; exit 0; fi
echo "$VER $SHA $(date +%Y-%m-%d) $MODE" > "$STAMP"
echo "==> recorded in .template-version"
