#!/usr/bin/env bash
#
# Writes or refreshes the stamped operating-notes block in agent files, from
# templates/operating-notes-tier{1..5}.md (AGENT_SECURITY_GUIDELINES.md §7).
# The block is never hand-edited: change the template, then re-stamp.
#
# Usage:
#
#     ./scripts/stamp-sections.sh categories/03-analysis-and-review/code-reviewer.md [more files...]
#
# There is no "stamp everything" default: with no paths it refuses, so a
# category is only touched by its own uplift.
#
# The stamp tier is chosen as CLAUDE.md, "Category tier and stamp tier",
# describes, and exactly as scripts/lint-agent-content.awk checks it:
#   1. a "<name>: tier=N" entry in scripts/lint-allowlist.txt, else
#   2. tier 1 when `tools` holds none of Bash, Write, Edit or NotebookEdit, else
#   3. the category tier, from the category directory number.
#
# An existing block is replaced in place. Otherwise the block goes after the
# "## Output" section, before the next H2 (Rollback, Approval gates) or at the
# end of the file. Running it twice changes nothing the second time.

set -uo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 1
allowlist="$repo/scripts/lint-allowlist.txt"

if [ "$#" -eq 0 ]; then
  printf 'Usage: %s <agent-file.md> [more files...]\n' "$0" >&2
  exit 1
fi

category_tier() {
  local num
  num=$(printf '%s' "$1" | sed -n 's#.*categories/\([0-9][0-9]\)-[^/]*/[^/]*$#\1#p')
  [ -n "$num" ] || { printf '0\n'; return; }
  num=$((10#$num))
  if [ "$num" -ge 1 ] && [ "$num" -le 6 ]; then printf '1\n'
  elif [ "$num" -le 13 ]; then printf '2\n'
  elif [ "$num" -le 17 ]; then printf '3\n'
  elif [ "$num" -le 21 ]; then printf '4\n'
  elif [ "$num" -le 24 ]; then printf '5\n'
  else printf '0\n'
  fi
}

frontmatter_value() {
  awk -v key="$2" '
    { sub(/\r$/, "") }
    NR == 1 && $0 != "---" { exit }
    NR > 1 && $0 == "---"  { exit }
    NR > 1 && index($0, key ":") == 1 {
      sub("^" key ": *", "")
      gsub(/^"|"$/, "")
      print
      exit
    }
  ' "$1"
}

stamp_override() {
  [ -f "$allowlist" ] || return 0
  awk -v n="$1" '
    { sub(/\r$/, ""); sub(/#.*/, "") }
    {
      p = index($0, ":")
      if (p == 0) next
      nm = substr($0, 1, p - 1); rl = substr($0, p + 1)
      gsub(/[ \t]/, "", nm); gsub(/[ \t]/, "", rl)
      if (nm == n && rl ~ /^tier=[1-5]$/) { print substr(rl, 6, 1); exit }
    }
  ' "$allowlist"
}

status=0

for file in "$@"; do
  if [ ! -f "$file" ]; then
    printf 'stamp-sections: %s does not exist\n' "$file" >&2
    status=1
    continue
  fi

  path="$(cd "$(dirname "$file")" && pwd)/$(basename "$file")"
  cat_tier=$(category_tier "$path")
  if [ "$cat_tier" -eq 0 ]; then
    printf "stamp-sections: %s isn't in a categories/NN-* directory\n" "$file" >&2
    status=1
    continue
  fi

  name=$(frontmatter_value "$file" name)
  tools=$(frontmatter_value "$file" tools)
  tier=$(stamp_override "$name")
  if [ -z "$tier" ]; then
    case ",${tools// /}," in
      *,Bash,* | *,Write,* | *,Edit,* | *,NotebookEdit,*) tier="$cat_tier" ;;
      *) tier=1 ;;
    esac
  fi

  template="$repo/templates/operating-notes-tier$tier.md"
  if [ ! -f "$template" ]; then
    printf 'stamp-sections: %s does not exist\n' "$template" >&2
    status=1
    continue
  fi

  # Markers inside fenced code are ignored, as the validator ignores them.
  if ! awk -v tmpl="$template" '
    BEGIN {
      while ((getline ln < tmpl) > 0) { sub(/\r$/, "", ln); T[++tn] = ln }
      BM = "<!-- BEGIN GENERATED: operating-notes tier="
      EM = "<!-- END GENERATED: operating-notes -->"
    }
    {
      sub(/\r$/, "")
      F[++n] = $0
      t = $0
      sub(/^[ \t]+/, "", t)
      if (fm < 2) { if ($0 == "---") fm++; next }
      if (infence) {
        r = t; k = 0
        while (substr(r, 1, 1) == fch) { k++; r = substr(r, 2) }
        gsub(/[ \t]/, "", r)
        if (k >= flen && r == "") infence = 0
        next
      }
      c = substr(t, 1, 1)
      if (c == "`" || c == "~") {
        r = t; k = 0
        while (substr(r, 1, 1) == c) { k++; r = substr(r, 2) }
        if (k >= 3) { infence = 1; fch = c; flen = k; next }
      }
      if (index($0, BM) == 1) { nbeg++; if (!b) b = n }
      if ($0 == EM) { nend++; if (b && !e) e = n }
      if ($0 == "## Output" && !out) out = n
      else if (out && !ins && $0 ~ /^## /) ins = n
    }
    END {
      if (nbeg || nend) {
        if (nbeg != 1 || nend != 1 || !e) {
          print "stamp-sections: " FILENAME ": expected one BEGIN and one END marker; fix by hand first" > "/dev/stderr"
          exit 2
        }
        for (i = 1; i < b; i++) print F[i]
        for (j = 1; j <= tn; j++) print T[j]
        for (i = e + 1; i <= n; i++) print F[i]
        exit 0
      }
      if (!out) {
        print "stamp-sections: " FILENAME ": no ## Output heading; add the skeleton first" > "/dev/stderr"
        exit 2
      }
      if (!ins) ins = n + 1
      last = ins - 1
      while (last > out && F[last] ~ /^[ \t]*$/) last--
      for (i = 1; i <= last; i++) print F[i]
      print ""
      for (j = 1; j <= tn; j++) print T[j]
      if (ins <= n) print ""
      for (i = ins; i <= n; i++) print F[i]
    }
  ' "$file" >"$file.stamp-tmp"; then
    rm -f "$file.stamp-tmp"
    status=1
    continue
  fi

  if cmp -s "$file" "$file.stamp-tmp"; then
    rm -f "$file.stamp-tmp"
    printf 'stamp-sections: %s already current (tier=%s)\n' "$file" "$tier"
  else
    mv "$file.stamp-tmp" "$file"
    printf 'stamp-sections: stamped %s (tier=%s)\n' "$file" "$tier"
  fi
done

exit "$status"
