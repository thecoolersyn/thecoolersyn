#!/usr/bin/env bash
#
# build.sh — validate every asset in this repo.
#
# GitHub renders README assets as images through its image proxy, and it
# silently strips <script>, <foreignObject> and inline event handlers. This
# script is the guard rail: it fails the build if any asset would break, get
# stripped, or bloat the page.
#
# Usage:
#   bash scripts/build.sh            # validate everything
#   bash scripts/build.sh --strict   # treat size warnings as failures too
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STRICT=0
[[ "${1:-}" == "--strict" ]] && STRICT=1

WARN_KB=40      # design-system target
HARD_KB=80      # hard ceiling — beyond this GitHub crawlers may time out

pass=0; warn=0; fail=0; missing=0
rows=()

hr() { printf '%s\n' "──────────────────────────────────────────────────────────────────"; }

# Patterns GitHub strips or that break image rendering.
FORBIDDEN=(
  '<script'
  'foreignObject'
  '@font-face'
  'onload='
  'onclick='
  'onerror='
  'javascript:'
)

check_file() {
  local f="$1"
  local base kb anim problems=()

  if [[ ! -f "$f" ]]; then
    printf '  %-42s %8s  %s\n' "$f" "—" "SKIP (not generated yet)"
    missing=$((missing + 1))
    return
  fi
  # 1. well-formed XML
  if ! python3 -c "import xml.dom.minidom,sys; xml.dom.minidom.parse(sys.argv[1])" "$f" 2>/dev/null; then
    problems+=("malformed XML")
  fi

  # 2. size budget
  local bytes; bytes=$(wc -c < "$f" | tr -d ' ')
  kb=$(( bytes / 1024 ))
  if   (( kb > HARD_KB )); then problems+=("size ${kb}KB > ${HARD_KB}KB hard limit")
  elif (( kb > WARN_KB )); then problems+=("size ${kb}KB > ${WARN_KB}KB target")
  fi

  # 3. things GitHub will strip
  local pat
  for pat in "${FORBIDDEN[@]}"; do
    if grep -qF -- "$pat" "$f"; then problems+=("contains '$pat'"); fi
  done

  # 4. external references (self-contained assets only)
  if grep -qE '(xlink:)?href="https?://' "$f"; then
    problems+=("external href reference")
  fi

  # 5. accessibility metadata
  grep -q 'role="img"' "$f" || problems+=("missing role=\"img\"")

  anim=$(grep -c '<animate' "$f" || true)

  local n=${#problems[@]}
  if (( n == 0 )); then
    printf '  %-42s %7sKB  %2s anim  PASS\n' "$f" "$kb" "$anim"
    pass=$((pass + 1))
  else
    local level="WARN" joined p
    joined=$(printf '%s; ' "${problems[@]}"); joined=${joined%; }
    for p in "${problems[@]}"; do
      case "$p" in
        size*) level="WARN"; [[ $STRICT -eq 1 ]] && level="FAIL" ;;
        *)     level="FAIL" ;;
      esac
    done
    case "$level" in
      FAIL) printf '  %-42s %7sKB  %2s anim  FAIL  %s\n' "$f" "$kb" "$anim" "$joined"
             fail=$((fail + 1)) ;;
      *)    printf '  %-42s %7sKB  %2s anim  WARN  %s\n' "$f" "$kb" "$anim" "$joined"
             warn=$((warn + 1)) ;;
    esac
  fi
}

echo
hr
echo "  ASSET VALIDATION — $ROOT"
hr

svg_list=$(find assets -name '*.svg' -not -path '*/live/*' | sort)
if [[ -z "$svg_list" ]]; then
  echo "  No SVG assets found under assets/."
else
  while IFS= read -r f; do
    [[ -n "$f" ]] && check_file "$f"
  done <<< "$svg_list"
fi

# ── README wiring ──────────────────────────────────────────────────────────
echo
hr
echo "  README REFERENCES"
hr
problems=0
refs=$(grep -oE 'src="assets/[^"]+"' README.md 2>/dev/null | sed 's/src="//;s/"$//' | sort -u)
if [[ -z "$refs" ]]; then
  echo "  (no asset references found in README.md)"
else
  while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    if [[ -e "$ref" ]]; then
      printf '  %-42s %s\n' "$ref" "found"
    else
      printf '  %-42s %s\n' "$ref" "MISSING — broken image on GitHub"
      problems=$((problems + 1))
    fi
  done <<< "$refs"
fi

# Placeholders that must be replaced before publishing.
ph=$(grep -c '⟦USERNAME⟧' README.md 2>/dev/null || true)
if [[ "${ph:-0}" -gt 0 ]]; then
  printf '  %-42s %s\n' "README placeholders" "$ph occurrence(s) of ⟦USERNAME⟧ — see docs/PLACEHOLDERS.md"
fi

# ── summary ────────────────────────────────────────────────────────────────
echo
hr
printf '  %d passed · %d warning(s) · %d failed · %d not generated · %d broken README ref(s)\n' \
  "$pass" "$warn" "$fail" "$missing" "$problems"
hr
echo

if (( fail > 0 || problems > 0 )); then
  echo "  BUILD FAILED"
  exit 1
fi
if (( STRICT == 1 && warn > 0 )); then
  echo "  BUILD FAILED (--strict: warnings are errors)"
  exit 1
fi
echo "  BUILD OK"
