#!/usr/bin/env bash
#
# Validates that the subagent catalog is internally consistent.
#
# Run from anywhere:
#
#     ./scripts/validate-catalog.sh
#
# Reports every failure it finds rather than stopping at the first, so one
# run tells you everything that needs fixing. Exits 0 when the catalog is
# clean, 1 otherwise.
#
# This script is the single source of truth for these checks: CI runs it via
# .github/workflows/validate.yml, and CLAUDE.md points at it rather than
# duplicating the logic.

set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

failures=0

fail() {
  printf 'FAIL  %s\n' "$1" >&2
  failures=$((failures + 1))
}

section() {
  printf '\n== %s\n' "$1"
}

agent_files() {
  find categories -name '*.md' ! -name 'README.md' | sort
}

# $1 = file, $2 = key. Reads only the frontmatter block and strips optional
# surrounding quotes from the value.
frontmatter_value() {
  awk -v key="$2" '
    NR == 1 && $0 != "---" { exit }
    NR > 1 && $0 == "---"  { exit }
    NR > 1 {
      if (index($0, key ":") == 1) {
        sub("^" key ": *", "")
        gsub(/^"|"$/, "")
        print
        exit
      }
    }
  ' "$1"
}

# ---------------------------------------------------------------------------
section 'Every agent file is listed in its category plugin.json'
# ---------------------------------------------------------------------------
# Compares file names rather than counts. A count-only check passes when one
# agent is listed under the wrong name and another is missing entirely.

for dir in categories/*/; do
  manifest="$dir.claude-plugin/plugin.json"

  if [ ! -f "$manifest" ]; then
    fail "$dir has no .claude-plugin/plugin.json"
    continue
  fi

  listed=$(grep -oE '"\./[^"]+\.md"' "$manifest" | tr -d '"' | sed 's|^\./||' | sort)
  actual=$(find "$dir" -maxdepth 1 -name '*.md' ! -name 'README.md' -exec basename {} \; | sort)

  while IFS= read -r name; do
    [ -n "$name" ] || continue
    grep -qxF "$name" <<<"$actual" || fail "$manifest lists ./$name but that file does not exist"
  done <<<"$listed"

  while IFS= read -r name; do
    [ -n "$name" ] || continue
    grep -qxF "$name" <<<"$listed" || fail "$dir$name is not listed in plugin.json"
  done <<<"$actual"
done

# ---------------------------------------------------------------------------
section 'Every agent file has all four required frontmatter keys'
# ---------------------------------------------------------------------------

while IFS= read -r file; do
  if [ "$(head -n 1 "$file" | tr -d '\r')" != "---" ]; then
    fail "$file does not open with a --- frontmatter fence"
    continue
  fi

  for key in name description tools model; do
    if [ -z "$(frontmatter_value "$file" "$key")" ]; then
      fail "$file is missing frontmatter key: $key"
    fi
  done
done < <(agent_files)

# ---------------------------------------------------------------------------
section 'Frontmatter name matches the filename'
# ---------------------------------------------------------------------------

while IFS= read -r file; do
  name=$(frontmatter_value "$file" name)
  base=$(basename "$file" .md)
  [ "$name" = "$base" ] && continue
  fail "$file declares name: $name (expected $base)"
done < <(agent_files)

# ---------------------------------------------------------------------------
section 'Agent names are unique across all categories'
# ---------------------------------------------------------------------------
# Claude Code resolves subagents by name, so the same name in two categories
# means one silently shadows the other once both plugins are installed.

while IFS= read -r name; do
  [ -n "$name" ] || continue
  locations=$(grep -rlx "name: $name" categories --include='*.md' | tr '\n' ' ')
  fail "agent name '$name' is used more than once: $locations"
done < <(while IFS= read -r file; do
  frontmatter_value "$file" name
done < <(agent_files) | sort | uniq -d)

# ---------------------------------------------------------------------------
section 'Every agent is documented in its category README'
# ---------------------------------------------------------------------------

while IFS= read -r file; do
  readme="$(dirname "$file")/README.md"
  base=$(basename "$file" .md)

  if [ ! -f "$readme" ]; then
    fail "$(dirname "$file") has no README.md"
    continue
  fi

  grep -qF "**$base**" "$readme" || fail "$base is not documented in $readme"
done < <(agent_files)

# ---------------------------------------------------------------------------
section 'Every agent is linked from the root README'
# ---------------------------------------------------------------------------
# Category 07 is the documented exception: the root README summarises it with
# a "View all 34 language specialists" link instead of itemising each agent.

while IFS= read -r file; do
  case "$file" in
    categories/07-language-and-framework-specialists/*) continue ;;
  esac

  grep -qF "($file)" README.md || fail "$file is not linked from the root README"
done < <(agent_files)

if ! grep -qF 'categories/07-language-and-framework-specialists/' README.md; then
  fail 'the root README no longer links to categories/07-language-and-framework-specialists/'
fi

# ---------------------------------------------------------------------------
section 'Root README category links resolve to real paths'
# ---------------------------------------------------------------------------

while IFS= read -r target; do
  [ -n "$target" ] || continue
  [ -e "$target" ] || fail "the root README links to $target, which does not exist"
done < <(grep -oE '\(categories/[^)]+\)' README.md | tr -d '()' | sed 's/#.*//' | sort -u)

# ---------------------------------------------------------------------------
section 'marketplace.json covers every category exactly once'
# ---------------------------------------------------------------------------

marketplace='.claude-plugin/marketplace.json'

if [ ! -f "$marketplace" ]; then
  fail "$marketplace does not exist"
else
  sources=$(grep -oE '"source": *"\./categories/[^"]+"' "$marketplace" |
    sed -E 's|.*"\./(categories/[^"]+)"|\1|' | sed 's|/$||' | sort)

  dirs=$(find categories -maxdepth 1 -mindepth 1 -type d | sed 's|/$||' | sort)

  while IFS= read -r source; do
    [ -n "$source" ] || continue
    [ -d "$source" ] || fail "$marketplace points at $source, which is not a directory"
  done <<<"$sources"

  while IFS= read -r dir; do
    [ -n "$dir" ] || continue
    grep -qxF "$dir" <<<"$sources" || fail "$dir has no entry in $marketplace"
  done <<<"$dirs"

  while IFS= read -r source; do
    [ -n "$source" ] || continue
    fail "$marketplace lists $source more than once"
  done < <(uniq -d <<<"$sources")
fi

# ---------------------------------------------------------------------------
section 'The advertised subagent count matches reality'
# ---------------------------------------------------------------------------

actual_count=$(agent_files | wc -l | tr -d '[:space:]')

badge_count=$(grep -oE 'badge/subagents-[0-9]+' README.md | head -n 1 | grep -oE '[0-9]+$')

if [ -z "$badge_count" ]; then
  fail 'could not find the subagent count badge in README.md'
elif [ "$badge_count" != "$actual_count" ]; then
  fail "the README badge says $badge_count subagents but the catalog holds $actual_count"
fi

marketplace_count=$(grep -oE 'Curated collection of [0-9]+' "$marketplace" 2>/dev/null | grep -oE '[0-9]+$')

if [ -z "$marketplace_count" ]; then
  fail "could not find the subagent count in the $marketplace description"
elif [ "$marketplace_count" != "$actual_count" ]; then
  fail "$marketplace says $marketplace_count subagents but the catalog holds $actual_count"
fi

# ---------------------------------------------------------------------------

printf '\n'

if [ "$failures" -ne 0 ]; then
  printf '%s check(s) failed.\n' "$failures" >&2
  exit 1
fi

printf 'Catalog is consistent: %s agent files across %s categories.\n' \
  "$actual_count" \
  "$(find categories -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d '[:space:]')"
