"""Body rules for scripts/agent_lint.py: stamp, opening, headings and markup.

check_body() takes the body as scripts/agent_lint.py scans it, a list of
BodyLine with fenced code already dropped, and reports through an Emit
callback. The rules key on the stamp tier, not the category tier.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field

from agent_file import BEGIN_MARK, BLANK_RE, END_MARK, Emit, one_stamp

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
ROW_NAMES = {row: heading for heading, row in FIXED_HEADINGS.items()}
ROW_NAMES[STAMP] = "the operating-notes stamp"
ROW_ORDER = (SCOPE, HOW, EXPERT, OUTPUT, STAMP, ROLLBACK, GATES)

# (row, stamp tiers that require it, stamp tiers that forbid it)
ALL_TIERS = frozenset(range(1, 6))
SECTION_RULES: tuple[tuple[int, frozenset[int], frozenset[int]], ...] = (
    (SCOPE, ALL_TIERS, frozenset()),
    (HOW, ALL_TIERS, frozenset()),
    (OUTPUT, ALL_TIERS, frozenset()),
    (EXPERT, frozenset({2, 3, 4, 5}), frozenset()),
    (ROLLBACK, frozenset({3, 4, 5}), frozenset({1})),
    (GATES, frozenset(), frozenset({1})),
)

LIST_ITEM_RE = re.compile(r"[ \t]*([-*+]|[0-9]+[.)])([ \t]|$)")
NUMBERED_ITEM_RE = re.compile(r"[0-9]+\. ")
SETEXT_RE = re.compile(r"( {1,3})?(=+|-+)[ \t]*$")
BOLD_ONLY_RE = re.compile(r"\*\*[^*]+\*\*:?[ \t]*$")
INDENTED_HASH_RE = re.compile(r" {1,3}#")
OPENING_RE = re.compile(r"You are an? ")
HEADING_TEXT_RE = re.compile(r" [^ \t]")


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


# -- Body lines --------------------------------------------------------------


@dataclass
class BodyLine:
    """A body line outside fenced code, or a fence's opening line."""

    text: str
    line_no: int
    fence: bool
    in_stamp: bool

    def is_h2(self) -> bool:
        """An H2 outside code, the boundary every section check stops at."""
        return not self.fence and self.text.startswith("## ")


@dataclass
class HeadingIndex:
    """The H2s _check_lines() found, as indexes into the body line list."""

    pos: dict[int, int] = field(default_factory=dict)  # skeleton row -> first
    domain: list[int] = field(default_factory=list)
    current_h2: str = ""


def check_body(
    body: list[BodyLine], stier: int, template: list[str] | None, emit: Emit
) -> None:
    """Stamp, markup, skeleton and section order, for stamp tier stier."""
    stamp_at = check_stamp(body, stier, template, emit)
    check_opening(body, emit)
    index = check_lines(body, emit)
    pos = index.pos
    check_how_you_work(body, pos, emit)
    check_sections(pos, stier, emit)
    if stamp_at is not None:
        pos[STAMP] = stamp_at
    check_order(body, pos, emit)
    check_domain_placement(body, pos, index.domain, stamp_at, emit)


# -- Skeleton ----------------------------------------------------------------


def check_sections(pos: dict[int, int], stier: int, emit: Emit) -> None:
    """Required, conditional and forbidden sections, by stamp tier."""
    for row, required, forbidden in SECTION_RULES:
        name = ROW_NAMES[row]
        if stier in required and row not in pos:
            always = required == ALL_TIERS
            emit(
                "C",
                "heading-missing",
                (
                    f"missing '{name}'"
                    if always
                    else f"stamp tier {stier} requires '{name}'"
                ),
            )
        if stier in forbidden and row in pos:
            emit("C", "heading-forbidden", f"stamp tier {stier} must not have '{name}'")


def check_order(body: list[BodyLine], pos: dict[int, int], emit: Emit) -> None:
    """The fixed headings in the skeleton's order."""
    last, last_row = -1, 0
    for row in (r for r in ROW_ORDER if r in pos):
        if pos[row] < last:
            emit(
                "C",
                "heading-order",
                f"line {body[pos[row]].line_no}: {ROW_NAMES[row]} comes before "
                f"{ROW_NAMES[last_row]}; the order is Scope, How you work, Expert "
                "practice, Output, operating notes, Rollback, Approval gates",
            )
        else:
            last, last_row = pos[row], row


def check_domain_placement(
    body: list[BodyLine],
    pos: dict[int, int],
    domain: list[int],
    stamp_at: int | None,
    emit: Emit,
) -> None:
    """Domain H2s sit between How you work and Expert practice (or Output).

    They never follow the stamp.
    """
    bounds = [b for b in (pos.get(EXPERT, pos.get(OUTPUT)), stamp_at) if b is not None]
    lower = pos.get(HOW)
    upper = min(bounds, default=None)
    for i in domain:
        below = lower is None or i < lower
        above = upper is not None and i > upper
        if below or above:
            emit(
                "C",
                "heading-order",
                f"line {body[i].line_no}: domain section '{body[i].text}' must sit "
                "between '## How you work' and '## Expert practice' "
                "(or '## Output')",
            )


# -- Stamp -------------------------------------------------------------------


def check_stamp(
    body: list[BodyLine], stier: int, template: list[str] | None, emit: Emit
) -> int | None:
    """Check the stamped block; return its BEGIN index when well-formed."""
    begins, ends = _stamp_markers(body)
    if not begins and not ends:
        emit(
            "C",
            "stamp-missing",
            "no operating-notes stamp; run scripts/stamp_sections.py",
        )
        return None
    if not one_stamp(begins, ends):
        emit(
            "F",
            "stamp-malformed",
            "expected exactly one BEGIN and one END operating-notes marker, "
            f"in that order; found {len(begins)} BEGIN and {len(ends)} END",
        )
        return None
    start, end = begins[0], ends[0]
    if [b.text for b in body[start : end + 1]] != template:
        emit(
            "F",
            "stamp-drift",
            f"line {body[start].line_no}: operating-notes block doesn't match "
            f"templates/operating-notes-tier{stier}.md (stamp tier {stier}); run "
            "scripts/stamp_sections.py",
        )
    after = next((b for b in body[end + 1 :] if not BLANK_RE.match(b.text)), None)
    if after is not None and not after.is_h2():
        emit(
            "C",
            "stamp-position",
            f"line {after.line_no}: only blank lines may sit between the END "
            "marker and the next H2",
        )
    return start


def _stamp_markers(body: list[BodyLine]) -> tuple[list[int], list[int]]:
    """Indexes of the BEGIN and END markers, outside code."""
    begins: list[int] = []
    ends: list[int] = []
    for i, b in enumerate(body):
        if b.fence:
            continue
        if b.text.startswith(BEGIN_MARK):
            begins.append(i)
        elif b.text == END_MARK:
            ends.append(i)
    return begins, ends


# -- Opening paragraph -------------------------------------------------------


def check_opening(body: list[BodyLine], emit: Emit) -> None:
    """One 'You are a(n) ...' paragraph, and nothing else, before the first H2.

    Stamp lines don't count. Extra content is reported once.
    """
    pre, first_h2 = _before_first_h2(body)
    opening = next((b for b in pre if not BLANK_RE.match(b.text)), None)
    if opening is None:
        msg = (
            f"line {first_h2.line_no}: no opening 'You are a(n) ...' paragraph "
            "before the first H2"
            if first_h2
            else "the body is empty"
        )
        emit("C", "opening-paragraph", msg)
        return
    if opening.fence or not OPENING_RE.match(opening.text):
        emit(
            "C",
            "opening-paragraph",
            f"line {opening.line_no}: the body must open with 'You are a(n) ...'",
        )
    extra = _first_extra_line(pre[pre.index(opening) + 1 :])
    if extra is not None:
        emit(
            "C",
            "opening-paragraph",
            f"line {extra.line_no}: only the opening paragraph may precede the "
            "first H2",
        )


def _before_first_h2(
    body: list[BodyLine],
) -> tuple[list[BodyLine], BodyLine | None]:
    """The non-stamp lines before the first H2, and that H2 if there is one."""
    pre: list[BodyLine] = []
    for b in body:
        if b.in_stamp:
            continue
        kind, level, _ = parse_heading(b.text)
        if not b.fence and kind == 1 and level == 2:
            return pre, b
        pre.append(b)
    return pre, None


def _first_extra_line(rest: list[BodyLine]) -> BodyLine | None:
    """The first line after the opening paragraph's first line that isn't part
    of it: anything after a blank line, a fence, or a heading."""
    seen_blank = False
    for b in rest:
        if BLANK_RE.match(b.text):
            seen_blank = True
        elif seen_blank or b.fence or parse_heading(b.text)[0] == 1:
            return b
    return None


# -- How you work ------------------------------------------------------------


def check_how_you_work(body: list[BodyLine], pos: dict[int, int], emit: Emit) -> None:
    """'## How you work' is a numbered list and nothing else."""
    if HOW not in pos:
        return
    lines = list(_section_content(body[pos[HOW] + 1 :]))
    if not lines:
        emit("C", "how-you-work", "'## How you work' holds no numbered list")
        return
    first, *rest = lines
    if not first.text.startswith("1. "):
        emit(
            "C",
            "how-you-work",
            f"line {first.line_no}: '## How you work' must open with '1. ': "
            f"{first.text}",
        )
    for b in rest:
        if not NUMBERED_ITEM_RE.match(b.text) and not b.text.startswith("   "):
            emit(
                "C",
                "how-you-work",
                f"line {b.line_no}: not a numbered item or a continuation indented "
                f"3+ spaces: {b.text}",
            )


def _section_content(rest: list[BodyLine]) -> Iterator[BodyLine]:
    """A section's non-blank lines up to the next H2 or the stamp.

    Headings are skipped: heading-h3 and heading-level report them.
    """
    for b in rest:
        if b.in_stamp or b.is_h2():
            return
        if BLANK_RE.match(b.text) or (not b.fence and b.text.startswith("#")):
            continue
        yield b


# -- Headings and markup, line by line ----------------------------------------


def check_lines(body: list[BodyLine], emit: Emit) -> HeadingIndex:
    """Markup and headings, line by line, stamp and code excluded."""
    index = HeadingIndex()
    prev = ""
    for i, b in enumerate(body):
        if b.in_stamp or b.fence:
            prev = ""
            continue
        check_markup(b, prev, emit)
        prev = b.text
        check_heading(i, b, index, emit)
    return index


def check_heading(i: int, b: BodyLine, index: HeadingIndex, emit: Emit) -> None:
    """Heading syntax and level; H2s are recorded in index."""
    s = b.text
    kind, level, text = parse_heading(s)
    if kind == 2:
        _check_run_in_heading(b, level, emit)
    elif kind != 1:
        return
    elif level == 1 or level >= 4:
        emit(
            "C",
            "heading-level",
            f"line {b.line_no}: H{level} is banned; use H2 or H3: {s}",
        )
    elif level == 2:
        check_h2(i, b, text, index, emit)
    else:
        _check_h3(b, text, index.current_h2, emit)


def _check_run_in_heading(b: BodyLine, level: int, emit: Emit) -> None:
    """'##Text': a near miss of a fixed heading, or a format error."""
    near = FIXED_BY_NORM.get(norm(b.text[level:])) if level == 2 else None
    if near:
        emit(
            "C",
            "heading-near-miss",
            f"line {b.line_no}: '{b.text}' is not exactly '{near}'",
        )
    else:
        emit(
            "C",
            "heading-format",
            f"line {b.line_no}: no space after the hashes: {b.text}",
        )


def _check_h3(b: BodyLine, text: str, current_h2: str, emit: Emit) -> None:
    """Spacing, and no H3 under How you work."""
    if not well_spaced(text):
        emit(
            "C",
            "heading-format",
            f"line {b.line_no}: use exactly one space after '###' and no "
            f"trailing space: '{b.text}'",
        )
    if current_h2 == "## How you work":
        emit(
            "C",
            "heading-h3",
            f"line {b.line_no}: no H3 under '## How you work': {b.text}",
        )


def check_h2(i: int, b: BodyLine, text: str, index: HeadingIndex, emit: Emit) -> None:
    """A fixed heading exactly as the skeleton spells it, or a domain one."""
    s = b.text
    index.current_h2 = s
    row = FIXED_HEADINGS.get(s)
    near = FIXED_BY_NORM.get(norm(text))
    if row == STAMP:
        emit(
            "C",
            "heading-operating-notes",
            f"line {b.line_no}: '## Operating notes' outside the stamped block",
        )
    elif row in index.pos:
        emit(
            "C", "heading-duplicate", f"line {b.line_no}: '{s}' appears more than once"
        )
    elif row is not None:
        index.pos[row] = i
    elif near:
        emit(
            "C", "heading-near-miss", f"line {b.line_no}: '{s}' is not exactly '{near}'"
        )
    else:
        if not well_spaced(text):
            emit(
                "C",
                "heading-format",
                f"line {b.line_no}: use exactly one space after '##' and no "
                f"trailing space: '{s}'",
            )
        index.domain.append(i)


def check_markup(b: BodyLine, prev: str, emit: Emit) -> None:
    """Setext headings, bold-only lines, HTML comments, indented headings."""
    s = b.text
    if SETEXT_RE.match(s) and _can_be_setext_title(prev):
        emit(
            "C",
            "heading-setext",
            f"line {b.line_no}: setext heading underline; use an ATX heading",
        )
    if BOLD_ONLY_RE.match(s):
        emit(
            "C",
            "bold-only-line",
            f"line {b.line_no}: a line of only bold text; use an H3: {s}",
        )
    if "<!--" in s and "<!-- TEMPLATE:" not in s:
        emit(
            "C",
            "html-comment",
            f"line {b.line_no}: the only HTML comments allowed are the stamp markers",
        )
    if INDENTED_HASH_RE.match(s) and parse_heading(s.strip(" \t"))[0] == 1:
        emit("C", "heading-format", f"line {b.line_no}: indented heading: {s}")


def _can_be_setext_title(prev: str) -> bool:
    """Whether a --- or === under prev makes prev a setext heading."""
    if not prev or BLANK_RE.match(prev):
        return False
    return parse_heading(prev)[0] != 1 and not LIST_ITEM_RE.match(prev)
