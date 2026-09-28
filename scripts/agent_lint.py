"""Per-file content lint for agent definitions (#318).

lint_file() applies the rules CLAUDE.md marks as linted under "Agent File
Format": frontmatter keys, values and per-tier rules; the body skeleton;
markup; the stamped operating notes; and banned content. CLAUDE.md states the
rules; this file and the two rule modules it calls are the enforcing copy,
and tests/test_agent_lint.py pins their behaviour. scripts/catalog_lint.py
runs it over the catalog and applies the ratchet; see its docstring for what
the finding classes C, F and W mean.

This module scans the file and checks banned content. The rules themselves
live in scripts/lint_frontmatter.py and scripts/lint_body.py. File reading
shared with scripts/stamp_sections.py lives in scripts/agent_file.py. Module
names use underscores, unlike the hyphenated shell scripts beside them, so
that they can be imported.

Standard library only: CI runs it with the runner's system Python.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from agent_file import (
    BEGIN_MARK,
    END_MARK,
    Allowlist,
    category_tier,
    closes_fence,
    fence_open,
    parse_frontmatter,
    split_lines,
    stamp_tier,
)
from lint_body import BodyLine, check_body, norm, parse_heading
from lint_frontmatter import check_frontmatter

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

# Banned wherever they appear, frontmatter and fenced code included:
# (rule, what it is, test on (line, lower-cased line)).
WHOLE_FILE_BANS = (
    (
        "template-leftover",
        "leftover template guidance",
        lambda s, low: s.startswith("# TEMPLATE:") or "<!-- TEMPLATE:" in s,
    ),
    (
        "banned-when-invoked",
        "'When invoked:' / 'On invocation:' label",
        lambda s, low: "When invoked:" in s or "On invocation:" in s,
    ),
    (
        "banned-emergency-stop",
        "EMERGENCY_STOP stop-file check",
        lambda s, low: "EMERGENCY_STOP" in s,
    ),
    (
        "banned-approval-gate",
        "generic approval gate (change ticket or read -p prompt)",
        lambda s, low: "change ticket" in low or "read -p" in s,
    ),
    (
        "banned-environment-preamble",
        "hand-written environment preamble, replaced by the stamped operating notes",
        lambda s, low: bool(ENV_PREAMBLE_RE.search(low)),
    ),
)


@dataclass(frozen=True)
class Finding:
    """One lint result."""

    cls: str  # C, F or W, as in scripts/catalog_lint.py's docstring
    rule: str
    path: str
    message: str


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
        check_frontmatter(fm, tier, self.allow, self.emit)
        stier = stamp_tier(fm.get("name"), fm.tool_set("tools"), tier, self.allow)
        check_body(body, stier, self.templates.get(stier), self.emit)
        return self.findings

    def _check_whole_file(self) -> None:
        """Banned content that is wrong wherever it appears."""
        for no, line in enumerate(self.lines, start=1):
            low = line.lower()
            for rule, what, banned in WHOLE_FILE_BANS:
                if banned(line, low):
                    self.emit("C", rule, f"line {no}: {what}: {line}")

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
            fence = fence_open(stripped)
            if fence:
                body.append(BodyLine(line, no, True, in_stamp))
                continue

            in_stamp = in_stamp or line.startswith(BEGIN_MARK)
            body.append(BodyLine(line, no, False, in_stamp))
            in_stamp = in_stamp and line != END_MARK
            if parse_heading(line)[0] == 1:
                section = line
                self._check_banned_heading(no, line)
            self._check_auto_approve(no, line, section)
            self._check_metric(no, line)
        return body

    def _check_banned_heading(self, no: int, line: str) -> None:
        """Headings retired by #354 and #315."""
        text = parse_heading(line)[2]
        if BANNED_HEADING_RE.fullmatch(norm(text)):
            self.emit("C", "banned-heading", f"line {no}: retired heading: {line}")
        elif text.strip(" \t") == "Approval Gates":
            self.emit(
                "C",
                "banned-heading",
                f"line {no}: retired generic heading "
                f"(the v3 heading is '## Approval gates'): {line}",
            )

    def _check_auto_approve(self, no: int, line: str, section: str) -> None:
        """-auto-approve has no place on a rollback path."""
        if "-auto-approve" in line and "rollback" in section.lower():
            self.emit(
                "C",
                "banned-auto-approve",
                f"line {no}: -auto-approve in a rollback path: {line}",
            )

    def _check_metric(self, no: int, line: str) -> None:
        """A heuristic, so a warning only: numbers the agent never measured."""
        low = line.lower()
        if any(r.search(low) for r in METRIC_RES):
            self.emit(
                "W",
                "metric-invented",
                f"line {no}: possible invented metric: {line}",
            )


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
