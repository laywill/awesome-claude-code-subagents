"""Banned-content rules: retired scaffolding, generic gates, invented metrics.

Functions over the parsed AgentDoc (scripts/lint_model.py), reporting
through an Emit callback. Unlike the body rules, some of these look inside
fenced code and frontmatter too, because the content is wrong wherever it
appears.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from lint_model import AgentDoc, BodyLine, Emit, HeadingKind, LineKind, Severity, norm

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

# Banned on any line of the file: (rule, what it is, test on the line and
# its lower-cased form).
LineTest = Callable[[str, str], bool]
WHOLE_FILE_BANS: tuple[tuple[str, str, LineTest], ...] = (
    (
        "template-leftover",
        "leftover template guidance",
        lambda s, _: s.startswith("# TEMPLATE:") or "<!-- TEMPLATE:" in s,
    ),
    (
        "banned-when-invoked",
        "'When invoked:' / 'On invocation:' label",
        lambda s, _: "When invoked:" in s or "On invocation:" in s,
    ),
    (
        "banned-emergency-stop",
        "EMERGENCY_STOP stop-file check",
        lambda s, _: "EMERGENCY_STOP" in s,
    ),
    (
        "banned-approval-gate",
        "generic approval gate (change ticket or read -p prompt)",
        lambda s, low: "change ticket" in low or "read -p" in s,
    ),
    (
        "banned-environment-preamble",
        "hand-written environment preamble, replaced by the stamped operating notes",
        lambda _, low: bool(ENV_PREAMBLE_RE.search(low)),
    ),
)


def check_whole_file(doc: AgentDoc, emit: Emit) -> None:
    """Bans that apply to every line: frontmatter, prose and code alike."""
    for no, line in enumerate(doc.lines, start=1):
        low = line.lower()
        for rule, what, banned in WHOLE_FILE_BANS:
            if banned(line, low):
                emit(Severity.RATCHETED, rule, f"line {no}: {what}: {line}")


def check_body_content(doc: AgentDoc, emit: Emit) -> None:
    """Retired headings and invented metrics in prose; -auto-approve in a
    rollback section, code included."""
    for b in doc.body:
        if b.kind is LineKind.FENCE:
            continue
        if b.heading.kind is HeadingKind.ATX:
            _check_banned_heading(b, emit)
        _check_auto_approve(b, emit)
        if b.kind is LineKind.PROSE and any(
            r.search(b.text.lower()) for r in METRIC_RES
        ):
            emit(
                Severity.WARN,
                "metric-invented",
                f"line {b.line_no}: possible invented metric: {b.text}",
            )


def _check_banned_heading(b: BodyLine, emit: Emit) -> None:
    """Headings retired by #354 and #315."""
    text = b.heading.text
    if BANNED_HEADING_RE.fullmatch(norm(text)):
        emit(
            Severity.RATCHETED,
            "banned-heading",
            f"line {b.line_no}: retired heading: {b.text}",
        )
    elif text.strip(" \t") == "Approval Gates":
        emit(
            Severity.RATCHETED,
            "banned-heading",
            f"line {b.line_no}: retired generic heading "
            f"(the v3 heading is '## Approval gates'): {b.text}",
        )


def _check_auto_approve(b: BodyLine, emit: Emit) -> None:
    """-auto-approve has no place on a rollback path."""
    if "-auto-approve" in b.text and "rollback" in b.section.lower():
        emit(
            Severity.RATCHETED,
            "banned-auto-approve",
            f"line {b.line_no}: -auto-approve in a rollback path: {b.text}",
        )
