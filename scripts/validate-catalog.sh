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

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

# Usage: ./scripts/validate-catalog.sh [--verbose] [category-dir ...]
#
# The content checks (issue #318) warn outside the categories listed in
# scripts/lint-enforced-categories.txt, and the pre-v3 catalog raises
# thousands of warnings. By default they print as counts by rule and by
# category. --verbose prints every warning; naming category directories
# (e.g. 03-analysis-and-review) prints every warning for those. Arguments
# change only what is printed, never what fails.

verbose=0
detail_categories=' '
for arg in "$@"; do
  case "$arg" in
    --verbose) verbose=1 ;;
    *) detail_categories+="${arg%/} " ;;
  esac
done

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
#
# Some agent files were committed with CRLF endings, which `* text=auto` in
# .gitattributes does not retroactively normalise — they stay CRLF on checkout
# even on Linux. Strip the CR first: gawk hides it in text mode but mawk, the
# default awk on ubuntu-latest, does not. Without this the fence comparison
# below never matches and every value reads back empty.
frontmatter_value() {
  awk -v key="$2" '
    { sub(/\r$/, "") }
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

while IFS= read -r dupe; do
  [ -n "$dupe" ] || continue

  # Resolved through frontmatter_value rather than grep -x, so a CRLF file
  # still reports its location instead of coming back empty.
  locations=$(while IFS= read -r file; do
    [ "$(frontmatter_value "$file" name)" = "$dupe" ] && printf '%s ' "$file"
  done < <(agent_files))

  fail "agent name '$dupe' is used more than once: $locations"
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
section 'Agent files carry no dead multi-agent scaffolding'
# ---------------------------------------------------------------------------
# Removed catalog-wide in #315. These sections referenced a context-manager
# agent and a message protocol that do not exist in Claude Code, and trained
# agents to report progress and metrics they never measured.
#
# The phrase list is deliberately narrow: python-pro legitimately discusses
# Python's `with`-statement context managers, so bare "context manager" is not
# banned.

banned_headings='^#+ *(Communication Protocol|Progress Tracking|Integration with Other Agents|Audit Logging) *$'
banned_phrases='requesting_agent|request_type|Delivery notification|^ *\**Progress tracking:|integration with other agents|query context manager|context manager for'

while IFS= read -r file; do
  while IFS= read -r hit; do
    [ -n "$hit" ] || continue
    fail "$file:${hit%%:*} has a banned heading: ${hit#*:}"
  done < <(grep -niE "$banned_headings" "$file")

  while IFS= read -r hit; do
    [ -n "$hit" ] || continue
    fail "$file:${hit%%:*} has banned scaffolding: ${hit#*:}"
  done < <(grep -niE "$banned_phrases" "$file")
done < <(agent_files)


# ---------------------------------------------------------------------------
section 'The content-lint ratchet and allowlist are well-formed'
# ---------------------------------------------------------------------------
# Enforced everywhere. A typo in either file would otherwise silently
# enforce nothing, or opt nothing out.

enforced_file='scripts/lint-enforced-categories.txt'
allowlist_file='scripts/lint-allowlist.txt'
declare -A enforced=()

if [ ! -f "$enforced_file" ]; then
  fail "$enforced_file does not exist"
else
  while IFS= read -r line; do
    line="${line%$'\r'}"
    line="${line%%#*}"
    line="${line//[[:space:]]/}"
    [ -n "$line" ] || continue
    if [ -d "categories/$line" ]; then
      enforced["$line"]=1
    else
      fail "$enforced_file lists $line, which is not a directory under categories/"
    fi
  done <"$enforced_file"
fi

if [ ! -f "$allowlist_file" ]; then
  fail "$allowlist_file does not exist"
else
  declare -A agent_tier=()
  while IFS= read -r file; do
    base=$(basename "$file" .md)
    num=${file#categories/}
    num=$((10#${num:0:2}))
    if [ "$num" -le 6 ]; then agent_tier["$base"]=1
    elif [ "$num" -le 13 ]; then agent_tier["$base"]=2
    elif [ "$num" -le 17 ]; then agent_tier["$base"]=3
    elif [ "$num" -le 21 ]; then agent_tier["$base"]=4
    else agent_tier["$base"]=5
    fi
  done < <(agent_files)

  declare -A seen_entry=()
  line_no=0
  while IFS= read -r line; do
    line_no=$((line_no + 1))
    line="${line%$'\r'}"
    trimmed="${line#"${line%%[![:space:]]*}"}"
    case "$trimmed" in
      '' | '#'*) continue ;;
    esac
    where="$allowlist_file:$line_no"
    if ! [[ "$line" =~ ^([a-z0-9-]+):[[:space:]]+([a-z0-9=-]+)[[:space:]]+#[[:space:]]*(.*)$ ]]; then
      fail "$where is not '<agent-name>: <rule> # <reason>': $line"
      continue
    fi
    entry_name="${BASH_REMATCH[1]}"
    entry_rule="${BASH_REMATCH[2]}"
    entry_reason="${BASH_REMATCH[3]}"
    [ -n "${entry_reason//[[:space:]]/}" ] || fail "$where has no reason after '#'"
    [ -z "${seen_entry[$entry_name:$entry_rule]:-}" ] || fail "$where repeats $entry_name: $entry_rule"
    seen_entry["$entry_name:$entry_rule"]=1

    entry_tier="${agent_tier[$entry_name]:-}"
    if [ -z "$entry_tier" ]; then
      fail "$where names $entry_name, which is not an agent in categories/"
      continue
    fi
    case "$entry_rule" in
      tier=[1-5]) ;;
      tier1-bash)
        [ "$entry_tier" -eq 1 ] || fail "$where: tier1-bash applies only to Tier 1 agents; $entry_name is Tier $entry_tier" ;;
      sonnet-instead-of-opus)
        [ "$entry_tier" -le 3 ] || fail "$where: sonnet-instead-of-opus applies only to Tier 1-3; Tier $entry_tier sonnet agents set effort: high anyway" ;;
      *) fail "$where: unknown rule '$entry_rule' (tier=N, tier1-bash or sonnet-instead-of-opus)" ;;
    esac
  done <"$allowlist_file"
fi

# ---------------------------------------------------------------------------
section 'Operating-notes templates match AGENT_SECURITY_GUIDELINES.md §7'
# ---------------------------------------------------------------------------
# §7 is the wording's source of truth; templates/ is what gets stamped. The
# N-th markdown code block in §7 is the tier-N block.

for tier in 1 2 3 4 5; do
  template="templates/operating-notes-tier$tier.md"
  if [ ! -f "$template" ]; then
    fail "$template does not exist"
    continue
  fi
  section7=$(awk -v want="$tier" '
    /^## 7\./ { s = 1; next }
    !inb && /^## / { s = 0 }
    s && /^```markdown$/ { n++; inb = 1; f = (n == want); next }
    s && /^```$/ { inb = 0; f = 0; next }
    f { print }
  ' AGENT_SECURITY_GUIDELINES.md)
  [ "$section7" = "$(cat "$template")" ] ||
    fail "$template differs from the tier $tier block in AGENT_SECURITY_GUIDELINES.md §7"
done

# ---------------------------------------------------------------------------
section 'Agent content: frontmatter, body skeleton, markup, stamp, banned content (#318)'
# ---------------------------------------------------------------------------
# The rules are CLAUDE.md's "Agent File Format"; scripts/lint-agent-content.awk
# is the enforcing copy. Each finding is ratcheted per category: FAIL in a
# category listed in scripts/lint-enforced-categories.txt, WARN elsewhere.
# Two exceptions: a stamped block that exists but is malformed or has drifted
# from its template always fails, and the invented-metric heuristic only
# ever warns.

warnings=0
declare -A warn_rule=()
declare -A warn_cat=()

while IFS=$'\t' read -r cls rule file msg; do
  cat="${file#categories/}"
  cat="${cat%%/*}"
  if [ "$cls" = F ] || { [ "$cls" = C ] && [ -n "${enforced[$cat]:-}" ]; }; then
    fail "$file: [$rule] $msg"
    continue
  fi
  warnings=$((warnings + 1))
  warn_rule["$rule"]=$((${warn_rule[$rule]:-0} + 1))
  warn_cat["$cat"]=$((${warn_cat[$cat]:-0} + 1))
  if [ "$verbose" -eq 1 ] || [[ "$detail_categories" == *" $cat "* ]]; then
    printf 'WARN  %s: [%s] %s\n' "$file" "$rule" "$msg"
  fi
done < <(agent_files | LC_ALL=C xargs awk -v allowfile="$allowlist_file" -v tmpldir=templates -f scripts/lint-agent-content.awk)

if [ "$warnings" -ne 0 ]; then
  printf 'Warnings by rule:\n'
  for rule in "${!warn_rule[@]}"; do
    printf '  %6s  %s\n' "${warn_rule[$rule]}" "$rule"
  done | sort -rn
  printf 'Warnings by category:\n'
  for cat in "${!warn_cat[@]}"; do
    printf '  %6s  %s\n' "${warn_cat[$cat]}" "$cat"
  done | sort -rn
  printf '%s warning(s), not enforced: pass --verbose or a category directory to list them.\n' "$warnings"
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
