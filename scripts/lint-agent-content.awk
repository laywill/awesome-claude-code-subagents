# Per-file content lint for agent definitions (issue #318).
#
# Called by scripts/validate-catalog.sh, never on its own:
#
#     LC_ALL=C awk -v allowfile=scripts/lint-allowlist.txt \
#                  -v tmpldir=templates \
#                  -f scripts/lint-agent-content.awk <agent files...>
#
# One pass over every agent file. The rules are the ones CLAUDE.md marks as
# linted under "Agent File Format": frontmatter keys, values and per-tier
# rules; the body skeleton; markup; the stamped operating notes; and banned
# content. CLAUDE.md states the rules; this file is the enforcing copy.
#
# Output is one finding per line, tab-separated:
#
#     <class> <rule> <file> <message>
#
# class C  content finding: FAIL in a category listed in
#          scripts/lint-enforced-categories.txt, WARN everywhere else
# class F  always FAIL: a stamped block that exists but is malformed or has
#          drifted from its template
# class W  always WARN: the invented-metric heuristic
#
# Portable to mawk (the default awk on ubuntu-latest): no gawk extensions,
# no regex interval expressions. Run under LC_ALL=C so length() counts bytes
# everywhere; description length strips UTF-8 continuation bytes to count
# characters.

function emit(cls, rule, msg) {
  printf "%s\t%s\t%s\t%s\n", cls, rule, cur, msg
}

function trim(s) {
  sub(/^[ \t]+/, "", s)
  sub(/[ \t]+$/, "", s)
  return s
}

function norm(s) {
  s = tolower(s)
  gsub(/[ \t]+/, " ", s)
  return trim(s)
}

function start_file() {
  cur = FILENAME
  state = "start"
  nb = 0
  nk = 0
  lastk = ""
  desc_multiline = 0
  infence = 0
  fch = ""
  flen = 0
  instamp = 0
  sect = ""
  split("", FM)
  split("", B)
  split("", L)
  split("", K)
  split("", S)
}

# Sets HL (level) and HT (text after the hashes, untrimmed). Returns 1 for an
# ATX heading, 2 for "##Text" (hashes with no space), 0 otherwise.
function hparse(s,    h, rest) {
  if (substr(s, 1, 1) != "#") return 0
  h = 0
  while (substr(s, h + 1, 1) == "#") h++
  rest = substr(s, h + 1)
  HL = h
  HT = rest
  if (rest == "" || rest ~ /^[ \t]/) return 1
  if (h >= 2) return 2
  return 0
}

function is_list_item(s) {
  return s ~ /^[ \t]*([-*+]|[0-9]+[.)])([ \t]|$)/
}

BEGIN {
  for (t = 1; t <= 5; t++) {
    f = tmpldir "/operating-notes-tier" t ".md"
    n = 0
    while ((getline ln < f) > 0) {
      sub(/\r$/, "", ln)
      n++
      T[t, n] = ln
    }
    close(f)
    TN[t] = n
  }

  # scripts/lint-allowlist.txt: "<name>: <rule> # <reason>". Well-formedness
  # is checked by scripts/validate-catalog.sh; here we only read it.
  while ((getline ln < allowfile) > 0) {
    sub(/\r$/, "", ln)
    if (ln ~ /^[ \t]*#/ || ln ~ /^[ \t]*$/) continue
    sub(/#.*/, "", ln)
    p = index(ln, ":")
    if (p == 0) continue
    nm = trim(substr(ln, 1, p - 1))
    rl = trim(substr(ln, p + 1))
    if (rl ~ /^tier=[1-5]$/) OV[nm] = substr(rl, 6, 1)
    else AL[nm, rl] = 1
  }
  close(allowfile)

  split("name description tools model color disallowedTools effort maxTurns", a, " ")
  for (i in a) ALLOWED[a[i]] = 1
  split("permissionMode hooks mcpServers initialPrompt", a, " ")
  for (i in a) FORBIDDEN[a[i]] = 1
  split("isolation memory skills background omitClaudeMd experimental", a, " ")
  for (i in a) NOTUSED[a[i]] = 1

  split("Agent AskUserQuestion Bash Edit ExitPlanMode Glob Grep LSP NotebookEdit PowerShell Read Skill Task TodoWrite WebFetch WebSearch Write", a, " ")
  for (i in a) REAL[a[i]] = 1

  COLOR[1] = "green"; COLOR[2] = "yellow"; COLOR[3] = "orange"; COLOR[4] = "red"; COLOR[5] = "purple"

  # Fixed headings, by Body skeleton row. Row 6 lives inside the stamp.
  FIXED["## Scope"] = 1
  FIXED["## How you work"] = 2
  FIXED["## Expert practice"] = 4
  FIXED["## Output"] = 5
  FIXED["## Operating notes"] = 6
  FIXED["## Rollback"] = 7
  FIXED["## Approval gates"] = 8
  for (h in FIXED) FIXNORM[norm(substr(h, 3))] = h
  ROWNAME[1] = "## Scope"; ROWNAME[2] = "## How you work"; ROWNAME[4] = "## Expert practice"
  ROWNAME[5] = "## Output"; ROWNAME[6] = "the operating-notes stamp"; ROWNAME[7] = "## Rollback"
  ROWNAME[8] = "## Approval gates"

  BEGIN_MARK = "<!-- BEGIN GENERATED: operating-notes tier="
  END_MARK = "<!-- END GENERATED: operating-notes -->"
  cur = ""
}

FNR == 1 {
  if (cur != "") finish_file()
  start_file()
}

{
  line = $0
  sub(/\r$/, "", line)
  low = tolower(line)

  # -- Whole-file checks: frontmatter, body and fenced code alike ---------
  if (line ~ /^# TEMPLATE:/ || index(line, "<!-- TEMPLATE:") > 0)
    emit("C", "template-leftover", "line " FNR ": leftover template guidance: " line)
  if (index(line, "When invoked:") > 0 || index(line, "On invocation:") > 0)
    emit("C", "banned-when-invoked", "line " FNR ": 'When invoked:' / 'On invocation:' label: " line)
  if (index(line, "EMERGENCY_STOP") > 0)
    emit("C", "banned-emergency-stop", "line " FNR ": EMERGENCY_STOP stop-file check: " line)
  if (index(low, "change ticket") > 0 || line ~ /read -p/)
    emit("C", "banned-approval-gate", "line " FNR ": generic approval gate (change ticket or read -p prompt): " line)
  if (low ~ /\*\*environment (note|adaptability)/)
    emit("C", "banned-environment-preamble", "line " FNR ": hand-written environment preamble, replaced by the stamped operating notes: " line)

  if (state == "start") {
    # No opening fence: the structural check in validate-catalog.sh fails
    # the file already, and nothing below can be read reliably.
    state = (line == "---") ? "fm" : "skip"
    next
  }
  if (state == "skip") next

  if (state == "fm") {
    if (line == "---") { state = "body"; next }
    if (line ~ /^[A-Za-z][A-Za-z0-9_]*:/) {
      k = line
      sub(/:.*/, "", k)
      v = line
      sub(/^[^:]*:[ \t]*/, "", v)
      v = trim(v)
      if (v ~ /^".*"$/ || v ~ /^'.*'$/) v = substr(v, 2, length(v) - 2)
      if (k in FM) emit("C", "frontmatter-duplicate-key", "frontmatter key '" k "' appears more than once")
      FM[k] = v
      KEYS[++nk] = k
      lastk = k
    } else if (line !~ /^[ \t]*(#|$)/ && lastk == "description") {
      desc_multiline = 1
    }
    next
  }

  # -- Body --------------------------------------------------------------
  t = line
  sub(/^[ \t]+/, "", t)

  if (infence) {
    r = t
    n = 0
    while (substr(r, 1, 1) == fch) { n++; r = substr(r, 2) }
    if (n >= flen && trim(r) == "") infence = 0
    else if (index(line, "-auto-approve") > 0 && tolower(sect) ~ /rollback/)
      emit("C", "banned-auto-approve", "line " FNR ": -auto-approve in a rollback path: " line)
    next
  }

  c = substr(t, 1, 1)
  if (c == "`" || c == "~") {
    r = t
    n = 0
    while (substr(r, 1, 1) == c) { n++; r = substr(r, 2) }
    if (n >= 3) {
      infence = 1
      fch = c
      flen = n
      nb++; B[nb] = line; L[nb] = FNR; K[nb] = "fence"; S[nb] = instamp
      next
    }
  }

  if (index(line, BEGIN_MARK) == 1) instamp = 1
  nb++; B[nb] = line; L[nb] = FNR; K[nb] = ""; S[nb] = instamp
  if (line == END_MARK) instamp = 0

  if (hparse(line) == 1) {
    sect = line
    x = norm(HT)
    if (x ~ /^(security safeguards|emergency stop.*|blast radius controls|input validation|rollback procedures|development workflow|environment note|environment adaptability.*)$/)
      emit("C", "banned-heading", "line " FNR ": retired heading: " line)
    else if (trim(HT) == "Approval Gates")
      emit("C", "banned-heading", "line " FNR ": retired generic heading (the v3 heading is '## Approval gates'): " line)
  }
  if (index(line, "-auto-approve") > 0 && tolower(sect) ~ /rollback/)
    emit("C", "banned-auto-approve", "line " FNR ": -auto-approve in a rollback path: " line)

  if (low ~ /[0-9]+ *% *(coverage|accuracy|confidence|success|uptime)/ ||
      low ~ /(coverage|accuracy|confidence|score|latency|uptime|success rate) *(of|is|at|:) *[<>]?=? *[0-9]/ ||
      low ~ /[<>]=? *[0-9]+ *(ms|sec|secs|seconds|min|mins|minutes)( |$)/)
    emit("W", "metric-invented", "line " FNR ": possible invented metric: " line)
}

END {
  if (cur != "") finish_file()
}

function finish_file(    cat, num, tier, name, desc, tools, dis, model, color, effort, mt, i, k, n, tok, TS, DS, ts, ov, stier) {
  if (state == "skip" || state == "start") return
  if (state == "fm") { emit("C", "frontmatter", "frontmatter has no closing ---"); return }

  cat = cur
  sub(/^categories\//, "", cat)
  sub(/\/.*/, "", cat)
  num = substr(cat, 1, 2)
  if (num !~ /^[0-9][0-9]$/) return
  num = num + 0
  if (num >= 1 && num <= 6) tier = 1
  else if (num <= 13) tier = 2
  else if (num <= 17) tier = 3
  else if (num <= 21) tier = 4
  else if (num <= 24) tier = 5
  else return

  name = FM["name"]; desc = FM["description"]; tools = FM["tools"]; dis = FM["disallowedTools"]
  model = FM["model"]; color = FM["color"]; effort = FM["effort"]; mt = FM["maxTurns"]

  # -- Frontmatter keys ----------------------------------------------------
  for (i = 1; i <= nk; i++) {
    k = KEYS[i]
    if (k in ALLOWED) continue
    if (k in FORBIDDEN) emit("C", "frontmatter-key", "'" k "' is forbidden: plugin agents ignore it")
    else if (k in NOTUSED) emit("C", "frontmatter-key", "'" k "' is a Claude Code field this catalog doesn't use")
    else emit("C", "frontmatter-key", "'" k "' is not a recognised key (Claude Code silently ignores misspellings)")
  }

  if (name !~ /^[a-z0-9]+(-[a-z0-9]+)*$/) emit("C", "name-format", "name '" name "' is not kebab-case")

  # -- description -------------------------------------------------------
  n = desc
  gsub(/[\200-\277]/, "", n)
  if (length(n) > 250) emit("C", "description-length", "description is " length(n) " characters, over the 250 limit")
  if (index(desc, "<example") > 0) emit("C", "description-format", "description holds an <example> block")
  if (desc_multiline || desc ~ /^[|>][-+]?$/ || index(desc, "\\n") > 0)
    emit("C", "description-format", "description spans more than one line")

  # -- model ---------------------------------------------------------------
  if (model != "haiku" && model != "sonnet" && model != "opus")
    emit("C", "model-value", "model '" model "' is not haiku, sonnet or opus")

  # -- tools / disallowedTools ---------------------------------------------
  split("", TS); split("", DS)
  n = split(tools, ts, ",")
  for (i = 1; i <= n; i++) {
    tok = trim(ts[i])
    if (tok == "") continue
    TS[tok] = 1
    if (index(tok, "(") > 0 || tok ~ /^mcp__/) emit("C", "tools-format", "tools holds a specifier or MCP pattern: " tok)
    else if (!(tok in REAL)) emit("C", "tools-format", "tools holds an unrecognised tool name: " tok)
  }
  n = split(dis, ts, ",")
  for (i = 1; i <= n; i++) {
    tok = trim(ts[i])
    if (tok == "") continue
    DS[tok] = 1
    if (index(tok, "(") > 0 || tok ~ /^mcp__/) emit("C", "tools-format", "disallowedTools holds a specifier or MCP pattern: " tok)
    else if (!(tok in REAL)) emit("C", "tools-format", "disallowedTools holds an unrecognised tool name: " tok)
    if (tok in TS) emit("C", "tools-overlap", "'" tok "' is in both tools and disallowedTools")
  }

  # -- Per-tier rules (category tier; overrides never change these) ---------
  if (color != COLOR[tier])
    emit("C", "color-tier", "color is '" (color == "" ? "<absent>" : color) "', tier " tier " requires '" COLOR[tier] "'")

  if (tier == 1) {
    if ("Bash" in TS) {
      if (!((name, "tier1-bash") in AL))
        emit("C", "tier1-bash", "tier 1 tools hold Bash with no tier1-bash entry in scripts/lint-allowlist.txt")
    } else if (!("Bash" in DS)) {
      emit("C", "tier1-bash", "tier 1 disallowedTools must list Bash")
    }
  }

  if (effort != "" && effort != "high")
    emit("C", "effort", "effort '" effort "' is not allowed; the only allowed value is high")
  if (effort != "" && (model == "haiku" || model == "opus"))
    emit("C", "effort", "effort must be absent on " model)
  if (tier >= 4 && model == "sonnet" && effort != "high")
    emit("C", "effort", "tier " tier " sonnet agents require effort: high")
  if (tier <= 3 && model == "sonnet" && effort != "" && !((name, "sonnet-instead-of-opus") in AL))
    emit("C", "effort", "tier " tier " sets effort without a sonnet-instead-of-opus entry in scripts/lint-allowlist.txt")

  if (mt != "" && mt !~ /^[1-9][0-9]*$/)
    emit("C", "maxturns", "maxTurns '" mt "' is not a positive integer")
  if (tier <= 3 && mt != "") emit("C", "maxturns", "tier " tier " must not set maxTurns")
  if (tier == 4 && mt != "40") emit("C", "maxturns", "tier 4 requires maxTurns: 40, got '" mt "'")
  if (tier == 5 && mt != "25") emit("C", "maxturns", "tier 5 requires maxTurns: 25, got '" mt "'")

  # -- Stamp tier (body) ---------------------------------------------------
  if (name in OV) stier = OV[name]
  else if (("Bash" in TS) || ("Write" in TS) || ("Edit" in TS) || ("NotebookEdit" in TS)) stier = tier
  else stier = 1

  check_body(stier)
}

function check_body(stier,    i, j, s, hb, he, nbeg, nend, drift, phase, pos, cnt, dom, nd, cur_h2, prev, pk, r, x, bound, how_end, first, order, oi, last, lastk2, k) {
  # -- Stamp ------------------------------------------------------------------
  hb = 0; he = 0; nbeg = 0; nend = 0
  for (i = 1; i <= nb; i++) {
    if (K[i] == "fence") continue
    if (index(B[i], BEGIN_MARK) == 1) { nbeg++; if (hb == 0) hb = i }
    if (B[i] == END_MARK) { nend++; if (he == 0 && hb > 0) he = i }
  }
  if (nbeg == 0 && nend == 0) {
    emit("C", "stamp-missing", "no operating-notes stamp; run scripts/stamp-sections.sh")
  } else if (nbeg != 1 || nend != 1 || he == 0) {
    emit("F", "stamp-malformed", "expected exactly one BEGIN and one END operating-notes marker, in that order; found " nbeg " BEGIN and " nend " END")
    hb = 0; he = 0
  } else {
    drift = (he - hb + 1 != TN[stier])
    for (j = 0; !drift && j <= he - hb; j++)
      if (B[hb + j] != T[stier, j + 1]) drift = 1
    if (drift)
      emit("F", "stamp-drift", "line " L[hb] ": operating-notes block doesn't match templates/operating-notes-tier" stier ".md (stamp tier " stier "); run scripts/stamp-sections.sh")
    for (i = he + 1; i <= nb; i++) {
      if (B[i] ~ /^[ \t]*$/) continue
      if (K[i] != "fence" && B[i] ~ /^## /) break
      emit("C", "stamp-position", "line " L[i] ": only blank lines may sit between the END marker and the next H2")
      break
    }
  }

  # -- Line by line ---------------------------------------------------------
  split("", pos); split("", cnt); split("", dom)
  nd = 0; phase = 0; cur_h2 = ""; prev = ""; pk = ""
  for (i = 1; i <= nb; i++) {
    s = B[i]
    if (S[i]) { prev = ""; continue }

    # Opening paragraph (row 0), and nothing else before ## Scope.
    if (phase < 3 || phase == 4) {
      if (s ~ /^[ \t]*$/) { if (phase == 1) phase = 2 }
      else if (K[i] != "fence" && hparse(s) == 1 && HL == 2) {
        if (phase == 0) emit("C", "opening-paragraph", "line " L[i] ": no opening 'You are a(n) ...' paragraph before the first H2")
        phase = 3
      }
      else if (phase == 0) {
        phase = 1
        if (K[i] == "fence" || s !~ /^You are an? /)
          emit("C", "opening-paragraph", "line " L[i] ": the body must open with 'You are a(n) ...'")
      } else if (phase == 2 || K[i] == "fence" || hparse(s) == 1) {
        if (phase != 4) emit("C", "opening-paragraph", "line " L[i] ": only the opening paragraph may precede the first H2")
        phase = 4
      }
    }

    if (K[i] == "fence") { prev = ""; continue }

    # Markup: setext headings, bold-only lines, HTML comments.
    if (s ~ /^(   |  | )?(=+|-+)[ \t]*$/ && prev != "" && prev !~ /^[ \t]*$/ && hparse(prev) != 1 && !is_list_item(prev))
      emit("C", "heading-setext", "line " L[i] ": setext heading underline; use an ATX heading")
    if (s ~ /^\*\*[^*]+\*\*:?[ \t]*$/)
      emit("C", "bold-only-line", "line " L[i] ": a line of only bold text; use an H3: " s)
    if (index(s, "<!--") > 0 && index(s, "<!-- TEMPLATE:") == 0)
      emit("C", "html-comment", "line " L[i] ": the only HTML comments allowed are the stamp markers")
    if (s ~ /^(   |  | )#/ && hparse(trim(s)) == 1)
      emit("C", "heading-format", "line " L[i] ": indented heading: " s)

    prev = s
    r = hparse(s)
    if (r == 2) {
      if (HL == 2 && (norm(substr(s, HL + 1)) in FIXNORM))
        emit("C", "heading-near-miss", "line " L[i] ": '" s "' is not exactly '" FIXNORM[norm(substr(s, HL + 1))] "'")
      else
        emit("C", "heading-format", "line " L[i] ": no space after the hashes: " s)
      continue
    }
    if (r != 1) continue

    if (HL == 1 || HL >= 4) {
      emit("C", "heading-level", "line " L[i] ": H" HL " is banned; use H2 or H3: " s)
      continue
    }

    x = norm(HT)
    if (HL == 2) {
      cur_h2 = s
      if (s in FIXED) {
        k = FIXED[s]
        if (k == 6) { emit("C", "heading-operating-notes", "line " L[i] ": '## Operating notes' outside the stamped block"); continue }
        cnt[k]++
        if (!(k in pos)) pos[k] = i
        else emit("C", "heading-duplicate", "line " L[i] ": '" s "' appears more than once")
        continue
      }
      if (x in FIXNORM) { emit("C", "heading-near-miss", "line " L[i] ": '" s "' is not exactly '" FIXNORM[x] "'"); continue }
      if (HT !~ /^ [^ \t]/ || HT ~ /[ \t]$/) emit("C", "heading-format", "line " L[i] ": use exactly one space after '##' and no trailing space: '" s "'")
      dom[++nd] = i
      continue
    }

    # H3
    if (HT !~ /^ [^ \t]/ || HT ~ /[ \t]$/) emit("C", "heading-format", "line " L[i] ": use exactly one space after '###' and no trailing space: '" s "'")
    if (cur_h2 == "## How you work") emit("C", "heading-h3", "line " L[i] ": no H3 under '## How you work': " s)
  }
  if (phase == 0) emit("C", "opening-paragraph", "the body is empty")

  # -- ## How you work: a numbered list and nothing else ---------------------
  if (2 in pos) {
    first = 1
    for (i = pos[2] + 1; i <= nb; i++) {
      s = B[i]
      if (S[i]) break
      if (K[i] != "fence" && s ~ /^## /) break
      if (s ~ /^[ \t]*$/) continue
      if (K[i] != "fence" && s ~ /^#/) continue   # reported as heading-h3 / heading-level
      if (first) {
        first = 0
        if (s !~ /^1\. /) emit("C", "how-you-work", "line " L[i] ": '## How you work' must open with '1. ': " s)
      } else if (s !~ /^[0-9]+\. / && s !~ /^   /) {
        emit("C", "how-you-work", "line " L[i] ": not a numbered item or a continuation indented 3+ spaces: " s)
      }
    }
    if (first) emit("C", "how-you-work", "'## How you work' holds no numbered list")
  }

  # -- Required, conditional and forbidden sections, by stamp tier ------------
  if (!(1 in pos)) emit("C", "heading-missing", "missing '## Scope'")
  if (!(2 in pos)) emit("C", "heading-missing", "missing '## How you work'")
  if (!(5 in pos)) emit("C", "heading-missing", "missing '## Output'")
  if (stier != 1 && !(4 in pos)) emit("C", "heading-missing", "stamp tier " stier " requires '## Expert practice'")
  if (stier >= 3 && !(7 in pos)) emit("C", "heading-missing", "stamp tier " stier " requires '## Rollback'")
  if (stier == 1 && (7 in pos)) emit("C", "heading-forbidden", "stamp tier 1 must not have '## Rollback'")
  if (stier == 1 && (8 in pos)) emit("C", "heading-forbidden", "stamp tier 1 must not have '## Approval gates'")

  # -- Order: Scope, How you work, Expert practice, Output, stamp, Rollback, Approval gates
  if (hb > 0) pos[6] = hb
  split("1 2 4 5 6 7 8", order, " ")
  last = 0; lastk2 = 0
  for (oi = 1; oi <= 7; oi++) {
    k = order[oi]
    if (!(k in pos)) continue
    if (pos[k] < last)
      emit("C", "heading-order", "line " L[pos[k]] ": " ROWNAME[k] " comes before " ROWNAME[lastk2] "; the order is Scope, How you work, Expert practice, Output, operating notes, Rollback, Approval gates")
    else { last = pos[k]; lastk2 = k }
  }

  # -- Domain H2s sit between How you work and Expert practice (or Output) ----
  bound = (4 in pos) ? pos[4] : ((5 in pos) ? pos[5] : 0)
  for (j = 1; j <= nd; j++) {
    i = dom[j]
    if (!(2 in pos) || i < pos[2] || (bound > 0 && i > bound) || (hb > 0 && i > hb))
      emit("C", "heading-order", "line " L[i] ": domain section '" B[i] "' must sit between '## How you work' and '## Expert practice' (or '## Output')")
  }
}
