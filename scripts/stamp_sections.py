#!/usr/bin/env python3
"""Write or refresh the stamped operating-notes block in agent files.

The block comes from templates/operating-notes-tier{1..5}.md, whose wording
is AGENT_SECURITY_GUIDELINES.md section 7. It is never hand-edited: change the
template, then re-stamp.

Usage:

    python3 scripts/stamp_sections.py <agent-file.md> [more files...]

There is no "stamp everything" default: with no paths it refuses, so a
category is only touched by its own uplift.

The stamp tier is chosen as CLAUDE.md, "Category tier and stamp tier",
describes, and exactly as scripts/agent_lint.py checks it (the two share
agent_file.stamp_tier):

    1. a "<name>: tier=N" entry in scripts/lint-allowlist.txt, else
    2. tier 1 when `tools` holds none of Bash, Write, Edit or NotebookEdit, else
    3. the category tier, from the category directory number.

An existing block is replaced in place. Otherwise the block goes after the
"## Output" section, before the next H2 (Rollback, Approval gates) or at the
end of the file. Running it twice changes nothing the second time. Output is
always LF-terminated.
"""

from __future__ import annotations

import sys
from pathlib import Path

from agent_file import (
    ALLOWLIST_FILE,
    BLANK_RE,
    ROOT,
    TEMPLATE_DIR,
    Allowlist,
    category_tier,
    parse_frontmatter,
    read_text,
    split_lines,
    stamp_tier,
)
from lint_model import AgentDoc, parse_lines


class StampError(Exception):
    """A file that can't be stamped without a hand fix first."""


def stamp(lines: list[str], template: list[str]) -> list[str]:
    """Return lines with the operating-notes block written or refreshed.

    The file is read through lint_model.parse_lines(), exactly as the lint
    reads it, so markers and headings inside fenced code are ignored.
    """
    doc = parse_lines(lines)
    markers = doc.stamp_markers()
    if not markers.present:
        return _insert(doc, template)
    if markers.span is None:
        raise StampError("expected one BEGIN and one END marker; fix by hand first")
    begin, end = markers.span
    # Line numbers are 1-based: a line's number is the index after it.
    return lines[: begin - 1] + template + lines[end:]


def _insert(doc: AgentDoc, template: list[str]) -> list[str]:
    """Add the block after the Output section: before the next H2, or at the end.

    Blank lines closing the Output section are replaced by exactly one.
    """
    lines = list(doc.lines)
    output = doc.h2_line("## Output")
    if output is None:
        raise StampError("no ## Output heading; add the skeleton first")
    next_h2 = doc.next_h2(output)
    insert = len(lines) if next_h2 is None else next_h2 - 1
    last = insert - 1
    while last >= output and BLANK_RE.match(lines[last]):
        last -= 1
    tail = ["", *lines[insert:]] if insert < len(lines) else []
    return [*lines[: last + 1], "", *template, *tail]


def stamp_file(path: Path, root: Path, allow: Allowlist) -> str:
    """Stamp one file in place; return the message to print."""
    cat_tier = category_tier(path.resolve().as_posix())
    if cat_tier is None:
        raise StampError("isn't in a categories/NN-* directory")
    text = read_text(path)
    lines = split_lines(text)
    fm = parse_frontmatter(lines)
    name = fm.get("name") if fm else ""
    tools = fm.tool_set("tools") if fm else []
    tier = stamp_tier(name, tools, cat_tier, allow)

    template_path = root / TEMPLATE_DIR / f"operating-notes-tier{tier}.md"
    if not template_path.is_file():
        raise StampError(f"{template_path} does not exist")
    new_lines = stamp(lines, split_lines(read_text(template_path)))

    new_text = "".join(line + "\n" for line in new_lines)
    if new_text == text:
        return f"stamp-sections: {path} already current (tier={tier})"
    path.write_bytes(new_text.encode("utf-8", "surrogateescape"))
    return f"stamp-sections: stamped {path} (tier={tier})"


def main(argv: list[str] | None = None) -> int:
    """Entry point; exits 1 when any file couldn't be stamped."""
    paths = sys.argv[1:] if argv is None else argv
    if not paths:
        print(
            "Usage: stamp_sections.py <agent-file.md> [more files...]", file=sys.stderr
        )
        return 1

    allow_path = ROOT / ALLOWLIST_FILE
    allow = (
        Allowlist.parse(read_text(allow_path)) if allow_path.is_file() else Allowlist()
    )

    status = 0
    for arg in paths:
        path = Path(arg)
        if not path.is_file():
            print(f"stamp-sections: {arg} does not exist", file=sys.stderr)
            status = 1
            continue
        try:
            print(stamp_file(path, ROOT, allow))
        except StampError as err:
            print(f"stamp-sections: {arg}: {err}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
