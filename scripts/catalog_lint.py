#!/usr/bin/env python3
"""Content lint for the whole catalog, with the per-category ratchet (#318).

Called by scripts/validate-catalog.sh, which passes its arguments through:

    python3 scripts/catalog_lint.py [--verbose] [category-dir ...]

It checks the ratchet and allowlist files, checks the operating-notes
templates against AGENT_SECURITY_GUIDELINES.md section 7, and runs the
per-file rules in scripts/agent_lint.py over every agent file. A finding's
class decides whether it fails:

    C   content finding: FAIL in a category listed in
        scripts/lint-enforced-categories.txt, WARN everywhere else
    F   always FAIL: a stamped block that exists but is malformed or has
        drifted from its template
    W   always WARN: the invented-metric heuristic

Outside the enforced categories the pre-v3 catalog raises thousands of
warnings, so by default they print as counts by rule and by category.
--verbose prints every warning; naming category directories (e.g.
03-analysis-and-review) prints every warning for those. Arguments change only
what is printed, never what fails.

Standard library only: CI runs it with the runner's system Python.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from collections import Counter
from pathlib import Path

from agent_file import (
    ALLOWLIST_FILE,
    ROOT,
    TEMPLATE_DIR,
    TIER_OVERRIDE_RE,
    Allowlist,
    category_tier,
    load_templates,
    read_text,
    split_lines,
)
from agent_lint import Finding, lint_file

ENFORCED_FILE = "scripts/lint-enforced-categories.txt"
GUIDELINES_FILE = "AGENT_SECURITY_GUIDELINES.md"
ALLOWLIST_RULES = ("tier=N", "tier1-bash", "sonnet-instead-of-opus")
ALLOWLIST_ENTRY_RE = re.compile(r"([a-z0-9-]+):\s+([a-z0-9=-]+)\s+#\s*(.*)")


# -- Checks --------------------------------------------------------------------


def parse_enforced(text: str) -> list[str]:
    """Category names from scripts/lint-enforced-categories.txt."""
    names = []
    for line in split_lines(text):
        name = re.sub(r"\s", "", line.split("#", 1)[0])
        if name:
            names.append(name)
    return names


def check_allowlist(text: str, agent_tiers: dict[str, int]) -> list[str]:
    """Failures for malformed, duplicate or misapplied allowlist entries."""
    failures = []
    seen: set[tuple[str, str]] = set()
    for no, line in enumerate(split_lines(text), start=1):
        if line.strip() == "" or line.strip().startswith("#"):
            continue
        where = f"{ALLOWLIST_FILE}:{no}"
        match = ALLOWLIST_ENTRY_RE.fullmatch(line)
        if not match:
            failures.append(f"{where} is not '<agent-name>: <rule> # <reason>': {line}")
            continue
        name, rule, reason = match.groups()
        if not reason.strip():
            failures.append(f"{where} has no reason after '#'")
        if (name, rule) in seen:
            failures.append(f"{where} repeats {name}: {rule}")
        seen.add((name, rule))
        if name not in agent_tiers:
            failures.append(
                f"{where} names {name}, which is not an agent in categories/"
            )
            continue
        problem = misapplied_rule(name, rule, agent_tiers[name])
        if problem:
            failures.append(f"{where}: {problem}")
    return failures


def misapplied_rule(name: str, rule: str, tier: int) -> str:
    """Why an allowlist rule can't apply to an agent of tier, or ""."""
    if TIER_OVERRIDE_RE.fullmatch(rule):
        return ""
    if rule == "tier1-bash":
        if tier != 1:
            return f"tier1-bash applies only to Tier 1 agents; {name} is Tier {tier}"
        return ""
    if rule == "sonnet-instead-of-opus":
        if tier > 3:
            return (
                "sonnet-instead-of-opus applies only to Tier 1-3; "
                f"Tier {tier} sonnet agents set effort: high anyway"
            )
        return ""
    return f"unknown rule '{rule}' ({', '.join(ALLOWLIST_RULES)})"


def guideline_blocks(text: str) -> list[list[str]]:
    """The markdown code blocks in AGENT_SECURITY_GUIDELINES.md section 7."""
    blocks: list[list[str]] = []
    in_section = in_block = False
    for line in split_lines(text):
        if line.startswith("## 7."):
            in_section = True
            continue
        if not in_block and line.startswith("## "):
            in_section = False
        if not in_section:
            continue
        if line == "```markdown":
            blocks.append([])
            in_block = True
        elif line == "```":
            in_block = False
        elif in_block:
            blocks[-1].append(line)
    return blocks


def check_templates(guidelines: str, templates: dict[int, list[str]]) -> list[str]:
    """Each template must match its tier's block in the guidelines, section 7."""
    failures = []
    blocks = guideline_blocks(guidelines)
    for tier in range(1, 6):
        template = f"{TEMPLATE_DIR}/operating-notes-tier{tier}.md"
        if tier not in templates:
            failures.append(f"{template} does not exist")
        elif tier > len(blocks) or blocks[tier - 1] != templates[tier]:
            failures.append(
                f"{template} differs from the tier {tier} block in {GUIDELINES_FILE} §7"
            )
    return failures


def ratchet(
    findings: list[Finding], enforced: set[str]
) -> tuple[list[Finding], list[Finding]]:
    """Split findings into (failures, warnings) by class and category."""
    failures, warnings = [], []
    for f in findings:
        category = f.path.removeprefix("categories/").split("/", 1)[0]
        if f.cls == "F" or (f.cls == "C" and category in enforced):
            failures.append(f)
        else:
            warnings.append(f)
    return failures, warnings


# -- Running over the repository ------------------------------------------------


def agent_files(root: Path) -> list[str]:
    """Repo-relative paths of every agent definition, sorted."""
    return sorted(
        p.relative_to(root).as_posix()
        for p in (root / "categories").rglob("*.md")
        if p.name != "README.md"
    )


class Reporter:
    """Prints sections and FAILs in validate-catalog.sh's format."""

    def __init__(self) -> None:
        self.failures = 0

    @staticmethod
    def section(title: str) -> None:
        """Start a titled section."""
        print(f"\n== {title}", flush=True)

    def fail(self, message: str) -> None:
        """Report one failure."""
        print(f"FAIL  {message}", file=sys.stderr, flush=True)
        self.failures += 1


def load_ratchet(
    root: Path, files: list[str], out: Reporter
) -> tuple[set[str], Allowlist]:
    """Read and check the enforced-categories file and the allowlist.

    Enforced everywhere: a typo in either file would otherwise silently
    enforce nothing, or opt nothing out.
    """
    agent_tiers = {
        Path(f).stem: tier for f in files if (tier := category_tier(f)) is not None
    }
    enforced: set[str] = set()
    enforced_path = root / ENFORCED_FILE
    if not enforced_path.is_file():
        out.fail(f"{ENFORCED_FILE} does not exist")
    else:
        for name in parse_enforced(read_text(enforced_path)):
            if (root / "categories" / name).is_dir():
                enforced.add(name)
            else:
                out.fail(
                    f"{ENFORCED_FILE} lists {name}, which is not a directory under "
                    "categories/"
                )

    allow = Allowlist()
    allow_path = root / ALLOWLIST_FILE
    if not allow_path.is_file():
        out.fail(f"{ALLOWLIST_FILE} does not exist")
    else:
        allow_text = read_text(allow_path)
        allow = Allowlist.parse(allow_text)
        for message in check_allowlist(allow_text, agent_tiers):
            out.fail(message)
    return enforced, allow


def run(root: Path, verbose: bool, detail: set[str]) -> int:
    """All content-lint checks for the repository at root; returns failures."""
    out = Reporter()
    files = agent_files(root)

    out.section("The content-lint ratchet and allowlist are well-formed")
    enforced, allow = load_ratchet(root, files, out)

    out.section(f"Operating-notes templates match {GUIDELINES_FILE} §7")
    # §7 is the wording's source of truth; templates/ is what gets stamped.
    # The N-th markdown code block in §7 is the tier-N block.
    templates = load_templates(root / TEMPLATE_DIR)
    for message in check_templates(read_text(root / GUIDELINES_FILE), templates):
        out.fail(message)

    out.section(
        "Agent content: frontmatter, body skeleton, markup, stamp, banned content "
        "(#318)"
    )
    findings = [
        finding
        for f in files
        for finding in lint_file(f, read_text(root / f), templates, allow)
    ]
    failures, warnings = ratchet(findings, enforced)
    for f in failures:
        out.fail(f"{f.path}: [{f.rule}] {f.message}")
    report_warnings(warnings, verbose, detail)

    return out.failures


def report_warnings(warnings: list[Finding], verbose: bool, detail: set[str]) -> None:
    """Print warnings in full where asked, and counts by rule and category."""
    if not warnings:
        return
    by_rule: Counter[str] = Counter()
    by_category: Counter[str] = Counter()
    for f in warnings:
        category = f.path.removeprefix("categories/").split("/", 1)[0]
        by_rule[f.rule] += 1
        by_category[category] += 1
        if verbose or category in detail:
            print(f"WARN  {f.path}: [{f.rule}] {f.message}")
    for title, counts in (("rule", by_rule), ("category", by_category)):
        print(f"Warnings by {title}:")
        for key, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {count:6d}  {key}")
    print(
        f"{len(warnings)} warning(s), not enforced: pass --verbose or a category "
        "directory to list them."
    )


def main(argv: list[str] | None = None) -> int:
    """Entry point; exits 1 when any check fails."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", 1)[0])
    parser.add_argument("--verbose", action="store_true", help="print every warning")
    parser.add_argument(
        "categories",
        nargs="*",
        help="category directories whose warnings to print in full",
    )
    args = parser.parse_args(argv)
    # Findings quote agent text, which can hold characters the console
    # encoding (cp1252 on Windows) or strict UTF-8 can't write.
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="backslashreplace")
    detail = {c.rstrip("/").removeprefix("categories/") for c in args.categories}
    failures = run(ROOT, args.verbose, detail)
    if failures:
        print(f"{failures} content check(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
