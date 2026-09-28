#!/usr/bin/env bash
#
# Promotes markdownlint and cspell from MegaLinter's report-only defaults
# (.mega-linter.yml DISABLE_ERRORS_LINTERS) to blocking, for just the
# categories listed in scripts/lint-enforced-categories.txt.
#
# MegaLinter's DISABLE_ERRORS_LINTERS is global for a linter -- it can't be
# scoped to a subset of files -- so this runs the same two tools directly,
# scoped to the enforced categories' own files (agent definitions and their
# README), against the same repo configs (.markdownlint.json, .cspell.json),
# and fails the build on any finding. Unlisted categories are unaffected:
# MegaLinter still reports on them in its own run, just without failing.
#
# Requires Node/npx, and network access on first run to fetch
# markdownlint-cli2 and cspell, pinned below so a release cannot change what
# blocks; bump deliberately.

set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

ENFORCED_FILE="scripts/lint-enforced-categories.txt"

mapfile -t categories < <(grep -vE '^[[:space:]]*(#|$)' "$ENFORCED_FILE" 2>/dev/null)

# Strip a lone CRLF remnant and blanks left by the mapfile/grep above.
clean_categories=()
for cat in "${categories[@]}"; do
  cat="${cat%$'\r'}"
  [ -n "$cat" ] && clean_categories+=("$cat")
done

if [ "${#clean_categories[@]}" -eq 0 ]; then
  printf 'lint-enforced-markdown: %s is empty, nothing to check.\n' "$ENFORCED_FILE"
  exit 0
fi

files=()
for cat in "${clean_categories[@]}"; do
  if [ ! -d "categories/$cat" ]; then
    printf 'lint-enforced-markdown: categories/%s does not exist\n' "$cat" >&2
    exit 1
  fi
  while IFS= read -r f; do
    files+=("$f")
  done < <(find "categories/$cat" -name '*.md' | sort)
done

printf 'lint-enforced-markdown: checking %s file(s) across %s enforced categories: %s\n' \
  "${#files[@]}" "${#clean_categories[@]}" "${clean_categories[*]}"

status=0

printf '\n== markdownlint (%s)\n' ".markdownlint.json"
if ! npx --yes markdownlint-cli2@0.23.3 --config .markdownlint.json "${files[@]}"; then
  status=1
fi

printf '\n== cspell (%s)\n' ".cspell.json"
if ! npx --yes cspell@10.3.5 --config .cspell.json --no-progress "${files[@]}"; then
  status=1
fi

exit "$status"
