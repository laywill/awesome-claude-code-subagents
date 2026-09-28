"""Per-file content lint for agent definitions (#318).

lint_file() applies the rules CLAUDE.md marks as linted under "Agent File
Format": frontmatter keys, values and per-tier rules; the body skeleton;
markup; the stamped operating notes; and banned content. CLAUDE.md states the
rules; the modules below are the enforcing copy, and tests/test_agent_lint.py
pins their behaviour. scripts/catalog_lint.py runs it over the catalog and
applies the ratchet.

The pipeline is parse, then validate:

    lint_model.py        parse_doc(): the file, parsed once, immutable
    lint_frontmatter.py  keys, values and tier rules
    lint_body.py         stamp, opening, headings, markup, skeleton
    lint_content.py      banned content

This module only wires them together. File reading shared with
scripts/stamp_sections.py lives in scripts/agent_file.py. Module names use
underscores, unlike the hyphenated shell scripts beside them, so that they
can be imported.

Standard library only: CI runs it with the runner's system Python.
"""

from __future__ import annotations

from dataclasses import dataclass

from agent_file import Allowlist, category_tier, stamp_tier
from lint_body import check_body
from lint_content import check_body_content, check_whole_file
from lint_frontmatter import check_frontmatter
from lint_model import Severity, parse_doc


@dataclass(frozen=True)
class Finding:
    """One lint result."""

    severity: Severity
    rule: str
    path: str
    message: str


def lint_file(
    path: str,
    text: str,
    templates: dict[int, list[str]],
    allow: Allowlist,
) -> list[Finding]:
    """Lint one agent file; return the findings in check order.

    path is the repo-relative, forward-slash path; it sets the category tier
    and is what findings report.
    """
    findings: list[Finding] = []

    def emit(severity: Severity, rule: str, message: str) -> None:
        findings.append(Finding(severity, rule, path, message))

    doc = parse_doc(text)
    check_whole_file(doc, emit)
    fm = doc.frontmatter
    if fm is None:
        # No opening fence: validate-catalog.sh fails the file already, and
        # nothing below can be read reliably.
        return findings
    for key in fm.duplicates:
        emit(
            Severity.RATCHETED,
            "frontmatter-duplicate-key",
            f"frontmatter key '{key}' appears more than once",
        )
    if not fm.closed:
        emit(Severity.RATCHETED, "frontmatter", "frontmatter has no closing ---")
        return findings
    check_body_content(doc, emit)
    tier = category_tier(path)
    if tier is None:
        return findings
    check_frontmatter(fm, tier, allow, emit)
    stier = stamp_tier(fm.get("name"), fm.tool_set("tools"), tier, allow)
    check_body(doc, stier, templates.get(stier), emit)
    return findings
