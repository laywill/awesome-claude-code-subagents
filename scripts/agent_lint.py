"""Per-file content lint for agent definitions (#318).

lint_file() applies the rules CLAUDE.md marks as linted under "Agent File
Format": frontmatter keys, values and per-tier rules; the body skeleton;
markup; the stamped operating notes; and banned content. CLAUDE.md states the
rules; this file is the enforcing copy, and tests/test_agent_lint.py pins its
behaviour. scripts/catalog_lint.py runs it over the catalog and applies the
ratchet; see its docstring for what the finding classes C, F and W mean.

File reading shared with scripts/stamp_sections.py lives in
scripts/agent_file.py. Module names use underscores, unlike the hyphenated
shell scripts beside them, so that they can be imported.

Standard library only: CI runs it with the runner's system Python.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from agent_file import (
    BEGIN_MARK,
    BLANK_RE,
    END_MARK,
    Allowlist,
    Frontmatter,
    category_tier,
    closes_fence,
    fence_open,
    parse_frontmatter,
    split_lines,
    stamp_tier,
)

ALLOWED_KEYS = {
    "name",
    "description",
    "tools",
    "model",
    "color",
    "disallowedTools",
    "effort",
    "maxTurns",
}
FORBIDDEN_KEYS = {"permissionMode", "hooks", "mcpServers", "initialPrompt"}
NOT_USED_KEYS = {
    "isolation",
    "memory",
    "skills",
    "background",
    "omitClaudeMd",
    "experimental",
}
REAL_TOOLS = {
    "Agent",
    "AskUserQuestion",
    "Bash",
    "Edit",
    "ExitPlanMode",
    "Glob",
    "Grep",
    "LSP",
    "NotebookEdit",
    "PowerShell",
    "Read",
    "Skill",
    "Task",
    "TodoWrite",
    "WebFetch",
    "WebSearch",
    "Write",
}
TIER_COLOR = {1: "green", 2: "yellow", 3: "orange", 4: "red", 5: "purple"}
TIER_MAX_TURNS = {4: "40", 5: "25"}

# Fixed headings, keyed by their row in CLAUDE.md's Body skeleton. Row 3 is
# the domain sections; row 6 lives inside the stamp.
SCOPE, HOW, EXPERT, OUTPUT, STAMP, ROLLBACK, GATES = 1, 2, 4, 5, 6, 7, 8
FIXED_HEADINGS = {
    "## Scope": SCOPE,
    "## How you work": HOW,
    "## Expert practice": EXPERT,
    "## Output": OUTPUT,
    "## Operating notes": STAMP,
    "## Rollback": ROLLBACK,
    "## Approval gates": GATES,
}
ROW_NAMES = {
    SCOPE: "## Scope",
    HOW: "## How you work",
    EXPERT: "## Expert practice",
    OUTPUT: "## Output",
    STAMP: "the operating-notes stamp",
    ROLLBACK: "## Rollback",
    GATES: "## Approval gates",
}
ROW_ORDER = (SCOPE, HOW, EXPERT, OUTPUT, STAMP, ROLLBACK, GATES)

NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
LIST_ITEM_RE = re.compile(r"[ \t]*([-*+]|[0-9]+[.)])([ \t]|$)")
SETEXT_RE = re.compile(r"( {1,3})?(=+|-+)[ \t]*$")
BOLD_ONLY_RE = re.compile(r"\*\*[^*]+\*\*:?[ \t]*$")
INDENTED_HASH_RE = re.compile(r" {1,3}#")
OPENING_RE = re.compile(r"You are an? ")
HEADING_TEXT_RE = re.compile(r" [^ \t]")
BANNED_HEADING_RE = re.compile(
    r"(security safeguards|emergency stop.*|blast radius controls"
    r"|input validation|rollback procedures|development workflow"
    r"|environment note|environment adaptability.*)"
)
ENV_PREAMBLE_RE = re.compile(r"\*\*environment (note|adaptability)")
METRIC_RES = (
    re.compile(r"[0-9]+ *% *(coverage|accuracy|confidence|success|uptime)"),
    re.compile(
        r"(coverage|accuracy|confidence|score|latency|uptime|success rate)"
        r" *(of|is|at|:) *[<>]?=? *[0-9]"
    ),
    re.compile(r"[<>]=? *[0-9]+ *(ms|sec|secs|seconds|min|mins|minutes)( |$)"),
)


# -- Headings --------------------------------------------------------------


def norm(text: str) -> str:
    """Lower-case and collapse whitespace, for near-miss heading matching."""
    return re.sub(r"[ \t]+", " ", text.lower()).strip(" \t")


# Fixed headings keyed by norm() of their text, to spot near misses.
FIXED_BY_NORM = {norm(h[3:]): h for h in FIXED_HEADINGS}


def well_spaced(text: str) -> bool:
    """Heading text after the hashes: exactly one space, no trailing space."""
    return bool(HEADING_TEXT_RE.match(text)) and not text.endswith((" ", "\t"))


def parse_heading(line: str) -> tuple[int, int, str]:
    """Classify an ATX heading.

    Returns (kind, level, text after the hashes). kind is 1 for a heading,
    2 for hashes run into text ("##Text", level 2 or more), 0 otherwise.
    """
    if not line.startswith("#"):
        return 0, 0, ""
    level = len(line) - len(line.lstrip("#"))
    rest = line[level:]
    if rest == "" or rest[0] in " \t":
        return 1, level, rest
    return (2 if level >= 2 else 0), level, rest


# -- Per-file lint ----------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """One lint result."""

    cls: str  # C, F or W, as in the module docstring
    rule: str
    path: str
    message: str


@dataclass
class BodyLine:
    """A body line outside fenced code, or a fence's opening line."""

    text: str
    line_no: int
    fence: bool
    in_stamp: bool


@dataclass
class HeadingIndex:
    """The H2s _check_lines() found, as indexes into the body line list."""

    pos: dict[int, int] = field(default_factory=dict)  # skeleton row -> first
    domain: list[int] = field(default_factory=list)
    current_h2: str = ""


class _FileLinter:
    """Lints one agent file. Use lint_file() rather than this directly."""

    def __init__(
        self,
        path: str,
        text: str,
        templates: dict[int, list[str]],
        allow: Allowlist,
    ) -> None:
        self.path = path
        self.lines = split_lines(text)
        self.templates = templates
        self.allow = allow
        self.findings: list[Finding] = []

    def emit(self, cls: str, rule: str, message: str) -> None:
        """Record a finding against this file."""
        self.findings.append(Finding(cls, rule, self.path, message))

    def run(self) -> list[Finding]:
        """Run every check and return the findings in file order."""
        self._check_whole_file()
        fm = parse_frontmatter(self.lines)
        if fm is None:
            # No opening fence: validate-catalog.sh fails the file already,
            # and nothing below can be read reliably.
            return self.findings
        for key in fm.duplicates:
            self.emit(
                "C",
                "frontmatter-duplicate-key",
                f"frontmatter key '{key}' appears more than once",
            )
        if not fm.closed:
            self.emit("C", "frontmatter", "frontmatter has no closing ---")
            return self.findings
        body = self._scan_body(fm.body_start)
        tier = category_tier(self.path)
        if tier is None:
            return self.findings
        self._check_frontmatter(fm, tier)
        stier = stamp_tier(fm.get("name"), fm.tool_set("tools"), tier, self.allow)
        self._check_body(body, stier)
        return self.findings

    # -- Lines anywhere in the file: frontmatter, body and fenced code alike

    def _check_whole_file(self) -> None:
        """Banned content that is wrong wherever it appears."""
        for no, line in enumerate(self.lines, start=1):
            low = line.lower()
            if line.startswith("# TEMPLATE:") or "<!-- TEMPLATE:" in line:
                self.emit(
                    "C",
                    "template-leftover",
                    f"line {no}: leftover template guidance: {line}",
                )
            if "When invoked:" in line or "On invocation:" in line:
                self.emit(
                    "C",
                    "banned-when-invoked",
                    f"line {no}: 'When invoked:' / 'On invocation:' label: {line}",
                )
            if "EMERGENCY_STOP" in line:
                self.emit(
                    "C",
                    "banned-emergency-stop",
                    f"line {no}: EMERGENCY_STOP stop-file check: {line}",
                )
            if "change ticket" in low or "read -p" in line:
                self.emit(
                    "C",
                    "banned-approval-gate",
                    f"line {no}: generic approval gate (change ticket or read -p "
                    f"prompt): {line}",
                )
            if ENV_PREAMBLE_RE.search(low):
                self.emit(
                    "C",
                    "banned-environment-preamble",
                    f"line {no}: hand-written environment preamble, replaced by the "
                    f"stamped operating notes: {line}",
                )

    # -- Body scan: builds the line list _check_body() walks -----------------

    def _scan_body(self, start: int) -> list[BodyLine]:
        """Walk the body once, collecting non-fenced lines and line checks.

        Lines inside fenced code are dropped, except that -auto-approve in a
        rollback section is banned inside code too.
        """
        body: list[BodyLine] = []
        fence: tuple[str, int] | None = None
        in_stamp = False
        section = ""
        for no, line in enumerate(self.lines[start:], start=start + 1):
            stripped = line.lstrip(" \t")
            if fence:
                if closes_fence(stripped, *fence):
                    fence = None
                else:
                    self._check_auto_approve(no, line, section)
                continue
            opened = fence_open(stripped)
            if opened:
                fence = opened
                body.append(BodyLine(line, no, True, in_stamp))
                continue

            if line.startswith(BEGIN_MARK):
                in_stamp = True
            body.append(BodyLine(line, no, False, in_stamp))
            if line == END_MARK:
                in_stamp = False

            kind, _, text = parse_heading(line)
            if kind == 1:
                section = line
                if BANNED_HEADING_RE.fullmatch(norm(text)):
                    self.emit(
                        "C", "banned-heading", f"line {no}: retired heading: {line}"
                    )
                elif text.strip(" \t") == "Approval Gates":
                    self.emit(
                        "C",
                        "banned-heading",
                        f"line {no}: retired generic heading "
                        f"(the v3 heading is '## Approval gates'): {line}",
                    )
            self._check_auto_approve(no, line, section)

            low = line.lower()
            if any(r.search(low) for r in METRIC_RES):
                self.emit(
                    "W",
                    "metric-invented",
                    f"line {no}: possible invented metric: {line}",
                )
        return body

    def _check_auto_approve(self, no: int, line: str, section: str) -> None:
        """-auto-approve has no place on a rollback path."""
        if "-auto-approve" in line and "rollback" in section.lower():
            self.emit(
                "C",
                "banned-auto-approve",
                f"line {no}: -auto-approve in a rollback path: {line}",
            )

    # -- Frontmatter ----------------------------------------------------------

    def _check_frontmatter(self, fm: Frontmatter, tier: int) -> None:
        """Keys, values and per-tier rules. Overrides never change these."""
        self._check_keys(fm)

        name = fm.get("name")
        if not NAME_RE.fullmatch(name):
            self.emit("C", "name-format", f"name '{name}' is not kebab-case")

        self._check_description(fm)

        model = fm.get("model")
        if model not in ("haiku", "sonnet", "opus"):
            self.emit(
                "C", "model-value", f"model '{model}' is not haiku, sonnet or opus"
            )

        tools = fm.tool_set("tools")
        disallowed = fm.tool_set("disallowedTools")
        self._check_tools(tools, disallowed)

        color = fm.get("color")
        if color != TIER_COLOR[tier]:
            self.emit(
                "C",
                "color-tier",
                f"color is '{color or '<absent>'}', tier {tier} requires "
                f"'{TIER_COLOR[tier]}'",
            )

        if tier == 1:
            self._check_tier1_bash(name, tools, disallowed)
        self._check_effort(name, model, fm.get("effort"), tier)
        self._check_max_turns(fm.get("maxTurns"), tier)

    def _check_keys(self, fm: Frontmatter) -> None:
        """Only the keys the catalog uses; misspellings are silently ignored."""
        for key in fm.keys:
            if key in ALLOWED_KEYS:
                continue
            if key in FORBIDDEN_KEYS:
                msg = f"'{key}' is forbidden: plugin agents ignore it"
            elif key in NOT_USED_KEYS:
                msg = f"'{key}' is a Claude Code field this catalog doesn't use"
            else:
                msg = (
                    f"'{key}' is not a recognised key "
                    "(Claude Code silently ignores misspellings)"
                )
            self.emit("C", "frontmatter-key", msg)

    def _check_tools(self, tools: list[str], disallowed: list[str]) -> None:
        """Real tool names, and none in both lists."""
        self._check_tool_names("tools", tools)
        self._check_tool_names("disallowedTools", disallowed)
        for tool in disallowed:
            if tool in tools:
                self.emit(
                    "C",
                    "tools-overlap",
                    f"'{tool}' is in both tools and disallowedTools",
                )

    def _check_tier1_bash(
        self, name: str, tools: list[str], disallowed: list[str]
    ) -> None:
        """Tier 1 disallows Bash unless the allowlist says the role needs it."""
        if "Bash" in tools:
            if not self.allow.allows(name, "tier1-bash"):
                self.emit(
                    "C",
                    "tier1-bash",
                    "tier 1 tools hold Bash with no tier1-bash entry in "
                    "scripts/lint-allowlist.txt",
                )
        elif "Bash" not in disallowed:
            self.emit("C", "tier1-bash", "tier 1 disallowedTools must list Bash")

    def _check_description(self, fm: Frontmatter) -> None:
        """One line, no examples, at most 250 characters."""
        desc = fm.get("description")
        if len(desc) > 250:
            self.emit(
                "C",
                "description-length",
                f"description is {len(desc)} characters, over the 250 limit",
            )
        if "<example" in desc:
            self.emit("C", "description-format", "description holds an <example> block")
        if (
            fm.description_multiline
            or re.fullmatch(r"[|>][-+]?", desc)
            or "\\n" in desc
        ):
            self.emit("C", "description-format", "description spans more than one line")

    def _check_tool_names(self, key: str, tools: list[str]) -> None:
        """Every entry is a plain, real tool name."""
        for tool in tools:
            if "(" in tool or tool.startswith("mcp__"):
                self.emit(
                    "C",
                    "tools-format",
                    f"{key} holds a specifier or MCP pattern: {tool}",
                )
            elif tool not in REAL_TOOLS:
                self.emit(
                    "C",
                    "tools-format",
                    f"{key} holds an unrecognised tool name: {tool}",
                )

    def _check_effort(self, name: str, model: str, effort: str, tier: int) -> None:
        """effort: high on Tier 4-5 sonnet, or an allowlisted Tier 1-3 sonnet."""
        if effort and effort != "high":
            self.emit(
                "C",
                "effort",
                f"effort '{effort}' is not allowed; the only allowed value is high",
            )
        if effort and model in ("haiku", "opus"):
            self.emit("C", "effort", f"effort must be absent on {model}")
        if tier >= 4 and model == "sonnet" and effort != "high":
            self.emit("C", "effort", f"tier {tier} sonnet agents require effort: high")
        if (
            tier <= 3
            and model == "sonnet"
            and effort
            and not self.allow.allows(name, "sonnet-instead-of-opus")
        ):
            self.emit(
                "C",
                "effort",
                f"tier {tier} sets effort without a sonnet-instead-of-opus entry in "
                "scripts/lint-allowlist.txt",
            )

    def _check_max_turns(self, max_turns: str, tier: int) -> None:
        """40 on Tier 4, 25 on Tier 5, absent below."""
        if max_turns and not re.fullmatch(r"[1-9][0-9]*", max_turns):
            self.emit(
                "C", "maxturns", f"maxTurns '{max_turns}' is not a positive integer"
            )
        if tier <= 3 and max_turns:
            self.emit("C", "maxturns", f"tier {tier} must not set maxTurns")
        if tier in TIER_MAX_TURNS and max_turns != TIER_MAX_TURNS[tier]:
            self.emit(
                "C",
                "maxturns",
                f"tier {tier} requires maxTurns: {TIER_MAX_TURNS[tier]}, got "
                f"'{max_turns}'",
            )

    # -- Body -------------------------------------------------------------------

    def _check_body(self, body: list[BodyLine], stier: int) -> None:
        """Stamp, markup, skeleton and section order."""
        stamp_at = self._check_stamp(body, stier)
        self._check_opening(body)
        index = self._check_lines(body)
        pos, domain = index.pos, index.domain
        self._check_how_you_work(body, pos)
        self._check_sections(pos, stier)
        if stamp_at is not None:
            pos[STAMP] = stamp_at
        self._check_order(body, pos, domain, stamp_at)

    def _check_sections(self, pos: dict[int, int], stier: int) -> None:
        """Required, conditional and forbidden sections, by stamp tier."""
        if SCOPE not in pos:
            self.emit("C", "heading-missing", "missing '## Scope'")
        if HOW not in pos:
            self.emit("C", "heading-missing", "missing '## How you work'")
        if OUTPUT not in pos:
            self.emit("C", "heading-missing", "missing '## Output'")
        if stier != 1 and EXPERT not in pos:
            self.emit(
                "C",
                "heading-missing",
                f"stamp tier {stier} requires '## Expert practice'",
            )
        if stier >= 3 and ROLLBACK not in pos:
            self.emit(
                "C", "heading-missing", f"stamp tier {stier} requires '## Rollback'"
            )
        if stier == 1 and ROLLBACK in pos:
            self.emit(
                "C", "heading-forbidden", "stamp tier 1 must not have '## Rollback'"
            )
        if stier == 1 and GATES in pos:
            self.emit(
                "C",
                "heading-forbidden",
                "stamp tier 1 must not have '## Approval gates'",
            )

    def _check_order(
        self,
        body: list[BodyLine],
        pos: dict[int, int],
        domain: list[int],
        stamp_at: int | None,
    ) -> None:
        """The skeleton's order, with domain H2s after How you work."""
        last, last_row = -1, 0
        for row in ROW_ORDER:
            if row not in pos:
                continue
            if pos[row] < last:
                self.emit(
                    "C",
                    "heading-order",
                    f"line {body[pos[row]].line_no}: {ROW_NAMES[row]} comes before "
                    f"{ROW_NAMES[last_row]}; the order is Scope, How you work, Expert "
                    "practice, Output, operating notes, Rollback, Approval gates",
                )
            else:
                last, last_row = pos[row], row

        # Domain H2s sit between How you work and Expert practice (or Output),
        # and never after the stamp.
        bounds = [
            b for b in (pos.get(EXPERT, pos.get(OUTPUT)), stamp_at) if b is not None
        ]
        upper = min(bounds, default=None)
        for i in domain:
            if HOW not in pos or i < pos[HOW] or (upper is not None and i > upper):
                self.emit(
                    "C",
                    "heading-order",
                    f"line {body[i].line_no}: domain section '{body[i].text}' must sit "
                    "between '## How you work' and '## Expert practice' "
                    "(or '## Output')",
                )

    def _check_stamp(self, body: list[BodyLine], stier: int) -> int | None:
        """Check the stamped block; return its BEGIN index when well-formed."""
        begins = [
            i
            for i, b in enumerate(body)
            if not b.fence and b.text.startswith(BEGIN_MARK)
        ]
        ends = [i for i, b in enumerate(body) if not b.fence and b.text == END_MARK]
        if not begins and not ends:
            self.emit(
                "C",
                "stamp-missing",
                "no operating-notes stamp; run scripts/stamp_sections.py",
            )
            return None
        if len(begins) != 1 or len(ends) != 1 or ends[0] < begins[0]:
            self.emit(
                "F",
                "stamp-malformed",
                "expected exactly one BEGIN and one END operating-notes marker, "
                f"in that order; found {len(begins)} BEGIN and {len(ends)} END",
            )
            return None
        start, end = begins[0], ends[0]
        if [b.text for b in body[start : end + 1]] != self.templates.get(stier):
            self.emit(
                "F",
                "stamp-drift",
                f"line {body[start].line_no}: operating-notes block doesn't match "
                f"templates/operating-notes-tier{stier}.md (stamp tier {stier}); run "
                "scripts/stamp_sections.py",
            )
        for b in body[end + 1 :]:
            if BLANK_RE.match(b.text):
                continue
            if not (not b.fence and b.text.startswith("## ")):
                self.emit(
                    "C",
                    "stamp-position",
                    f"line {b.line_no}: only blank lines may sit between the END "
                    "marker and the next H2",
                )
            break
        return start

    def _check_lines(self, body: list[BodyLine]) -> HeadingIndex:
        """Markup and headings, line by line, stamp and code excluded."""
        index = HeadingIndex()
        prev = ""
        for i, b in enumerate(body):
            if b.in_stamp or b.fence:
                prev = ""
                continue
            self._check_markup(b, prev)
            prev = b.text
            self._check_heading(i, b, index)
        return index

    def _check_heading(self, i: int, b: BodyLine, index: HeadingIndex) -> None:
        """Heading syntax and level; H2s are recorded in index."""
        s = b.text
        kind, level, text = parse_heading(s)
        if kind == 2:
            near = FIXED_BY_NORM.get(norm(s[level:])) if level == 2 else None
            if near:
                self.emit(
                    "C",
                    "heading-near-miss",
                    f"line {b.line_no}: '{s}' is not exactly '{near}'",
                )
            else:
                self.emit(
                    "C",
                    "heading-format",
                    f"line {b.line_no}: no space after the hashes: {s}",
                )
            return
        if kind != 1:
            return
        if level == 1 or level >= 4:
            self.emit(
                "C",
                "heading-level",
                f"line {b.line_no}: H{level} is banned; use H2 or H3: {s}",
            )
            return
        if level == 2:
            self._check_h2(i, b, text, index)
            return
        if not well_spaced(text):
            self.emit(
                "C",
                "heading-format",
                f"line {b.line_no}: use exactly one space after '###' and no "
                f"trailing space: '{s}'",
            )
        if index.current_h2 == "## How you work":
            self.emit(
                "C",
                "heading-h3",
                f"line {b.line_no}: no H3 under '## How you work': {s}",
            )

    def _check_h2(self, i: int, b: BodyLine, text: str, index: HeadingIndex) -> None:
        """A fixed heading exactly as the skeleton spells it, or a domain one."""
        s = b.text
        index.current_h2 = s
        row = FIXED_HEADINGS.get(s)
        if row == STAMP:
            self.emit(
                "C",
                "heading-operating-notes",
                f"line {b.line_no}: '## Operating notes' outside the stamped block",
            )
        elif row is not None:
            if row in index.pos:
                self.emit(
                    "C",
                    "heading-duplicate",
                    f"line {b.line_no}: '{s}' appears more than once",
                )
            else:
                index.pos[row] = i
        elif norm(text) in FIXED_BY_NORM:
            self.emit(
                "C",
                "heading-near-miss",
                f"line {b.line_no}: '{s}' is not exactly "
                f"'{FIXED_BY_NORM[norm(text)]}'",
            )
        else:
            if not well_spaced(text):
                self.emit(
                    "C",
                    "heading-format",
                    f"line {b.line_no}: use exactly one space after '##' and no "
                    f"trailing space: '{s}'",
                )
            index.domain.append(i)

    def _check_markup(self, b: BodyLine, prev: str) -> None:
        """Setext headings, bold-only lines, HTML comments, indented headings."""
        s = b.text
        if (
            SETEXT_RE.match(s)
            and prev
            and not BLANK_RE.match(prev)
            and parse_heading(prev)[0] != 1
            and not LIST_ITEM_RE.match(prev)
        ):
            self.emit(
                "C",
                "heading-setext",
                f"line {b.line_no}: setext heading underline; use an ATX heading",
            )
        if BOLD_ONLY_RE.match(s):
            self.emit(
                "C",
                "bold-only-line",
                f"line {b.line_no}: a line of only bold text; use an H3: {s}",
            )
        if "<!--" in s and "<!-- TEMPLATE:" not in s:
            self.emit(
                "C",
                "html-comment",
                f"line {b.line_no}: the only HTML comments allowed are the "
                "stamp markers",
            )
        if INDENTED_HASH_RE.match(s) and parse_heading(s.strip(" \t"))[0] == 1:
            self.emit("C", "heading-format", f"line {b.line_no}: indented heading: {s}")

    def _check_how_you_work(self, body: list[BodyLine], pos: dict[int, int]) -> None:
        """'## How you work' is a numbered list and nothing else."""
        if HOW not in pos:
            return
        first = True
        for b in body[pos[HOW] + 1 :]:
            s = b.text
            if b.in_stamp or (not b.fence and s.startswith("## ")):
                break
            if BLANK_RE.match(s):
                continue
            if not b.fence and s.startswith("#"):
                continue  # reported as heading-h3 / heading-level
            if first:
                first = False
                if not s.startswith("1. "):
                    self.emit(
                        "C",
                        "how-you-work",
                        f"line {b.line_no}: '## How you work' must open with "
                        f"'1. ': {s}",
                    )
            elif not re.match(r"[0-9]+\. ", s) and not s.startswith("   "):
                self.emit(
                    "C",
                    "how-you-work",
                    f"line {b.line_no}: not a numbered item or a continuation indented "
                    f"3+ spaces: {s}",
                )
        if first:
            self.emit("C", "how-you-work", "'## How you work' holds no numbered list")

    def _check_opening(self, body: list[BodyLine]) -> None:
        """One 'You are a(n) ...' paragraph, and nothing else, before the first H2.

        Stamp lines don't count. Extra content is reported once.
        """
        state = "before"  # then "paragraph", "after-paragraph", "reported"
        for b in body:
            s = b.text
            if b.in_stamp:
                continue
            if BLANK_RE.match(s):
                if state == "paragraph":
                    state = "after-paragraph"
                continue
            kind, level, _ = parse_heading(s)
            if not b.fence and kind == 1 and level == 2:
                if state == "before":
                    self.emit(
                        "C",
                        "opening-paragraph",
                        f"line {b.line_no}: no opening 'You are a(n) ...' paragraph "
                        "before the first H2",
                    )
                return
            if state == "before":
                state = "paragraph"
                if b.fence or not OPENING_RE.match(s):
                    self.emit(
                        "C",
                        "opening-paragraph",
                        f"line {b.line_no}: the body must open with 'You are a(n) ...'",
                    )
            elif state in ("after-paragraph", "reported") or b.fence or kind == 1:
                if state != "reported":
                    self.emit(
                        "C",
                        "opening-paragraph",
                        f"line {b.line_no}: only the opening paragraph may precede "
                        "the first H2",
                    )
                state = "reported"
        if state == "before":
            self.emit("C", "opening-paragraph", "the body is empty")


def lint_file(
    path: str,
    text: str,
    templates: dict[int, list[str]],
    allow: Allowlist,
) -> list[Finding]:
    """Lint one agent file.

    path is the repo-relative, forward-slash path; it sets the category tier
    and is what findings report.
    """
    return _FileLinter(path, text, templates, allow).run()
