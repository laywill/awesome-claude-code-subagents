"""Body rules: the stamp, the opening paragraph, headings, markup and skeleton.

Every rule is a function over the parsed AgentDoc (scripts/lint_model.py)
and reports through an Emit callback. The rules key on the stamp tier, not
the category tier. Positions are file line numbers throughout.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator

from lint_model import (
    FIXED_BY_NORM,
    FIXED_HEADINGS,
    ROW_NAMES,
    AgentDoc,
    BodyLine,
    Emit,
    HeadingKind,
    LineKind,
    Row,
    Severity,
    Skeleton,
    index_skeleton,
    norm,
    parse_heading,
)

C, F = Severity.RATCHETED, Severity.FAIL

ALL_TIERS = frozenset(range(1, 6))
# (row, stamp tiers that require it, stamp tiers that forbid it)
SECTION_RULES: tuple[tuple[Row, frozenset[int], frozenset[int]], ...] = (
    (Row.SCOPE, ALL_TIERS, frozenset()),
    (Row.HOW, ALL_TIERS, frozenset()),
    (Row.OUTPUT, ALL_TIERS, frozenset()),
    (Row.EXPERT, frozenset({2, 3, 4, 5}), frozenset()),
    (Row.ROLLBACK, frozenset({3, 4, 5}), frozenset({1})),
    (Row.GATES, frozenset(), frozenset({1})),
)

LIST_ITEM_RE = re.compile(r"[ \t]*([-*+]|[0-9]+[.)])([ \t]|$)")
NUMBERED_ITEM_RE = re.compile(r"[0-9]+\. ")
SETEXT_RE = re.compile(r"( {1,3})?(=+|-+)[ \t]*$")
BOLD_ONLY_RE = re.compile(r"\*\*[^*]+\*\*:?[ \t]*$")
INDENTED_HASH_RE = re.compile(r" {1,3}#")
OPENING_RE = re.compile(r"You are an? ")
HEADING_TEXT_RE = re.compile(r" [^ \t]")


def check_body(
    doc: AgentDoc, stier: int, template: list[str] | None, emit: Emit
) -> None:
    """Every body rule, for stamp tier stier and its template."""
    stamp_at = check_stamp(doc, stier, template, emit)
    skeleton = index_skeleton(doc, stamp_at)
    check_opening(doc, emit)
    check_lines(doc, skeleton, emit)
    check_how_you_work(doc, skeleton, emit)
    check_sections(skeleton, stier, emit)
    check_order(skeleton, emit)
    check_domain_placement(skeleton, emit)


# -- Stamp -------------------------------------------------------------------


def check_stamp(
    doc: AgentDoc, stier: int, template: list[str] | None, emit: Emit
) -> int | None:
    """Check the stamped block; return its BEGIN line when well-formed."""
    markers = doc.stamp_markers()
    if not markers.present:
        emit(
            C,
            "stamp-missing",
            "no operating-notes stamp; run scripts/stamp_sections.py",
        )
        return None
    if markers.span is None:
        emit(
            F,
            "stamp-malformed",
            "expected exactly one BEGIN and one END operating-notes marker, in that "
            f"order; found {len(markers.begins)} BEGIN and {len(markers.ends)} END",
        )
        return None
    start, end = markers.span
    block = [b.text for b in doc.prose if start <= b.line_no <= end]
    if block != template:
        emit(
            F,
            "stamp-drift",
            f"line {start}: operating-notes block doesn't match "
            f"templates/operating-notes-tier{stier}.md (stamp tier {stier}); run "
            "scripts/stamp_sections.py",
        )
    _check_after_stamp(doc, end, emit)
    return start


def _check_after_stamp(doc: AgentDoc, end: int, emit: Emit) -> None:
    """Only blank lines between the END marker and the next H2."""
    after = next((b for b in doc.prose if b.line_no > end and not b.blank), None)
    if after is not None and not after.is_h2:
        emit(
            C,
            "stamp-position",
            f"line {after.line_no}: only blank lines may sit between the END "
            "marker and the next H2",
        )


# -- Opening paragraph -------------------------------------------------------


def check_opening(doc: AgentDoc, emit: Emit) -> None:
    """One 'You are a(n) ...' paragraph, and nothing else, before the first H2.

    Stamp lines don't count. Extra content is reported once.
    """
    pre, first_h2 = _before_first_h2(doc.prose)
    content = [b for b in pre if not b.blank]
    if not content:
        emit(
            C,
            "opening-paragraph",
            (
                f"line {first_h2.line_no}: no opening 'You are a(n) ...' paragraph "
                "before the first H2"
                if first_h2
                else "the body is empty"
            ),
        )
        return
    opening = content[0]
    if opening.kind is LineKind.FENCE or not OPENING_RE.match(opening.text):
        emit(
            C,
            "opening-paragraph",
            f"line {opening.line_no}: the body must open with 'You are a(n) ...'",
        )
    extra = _first_extra_line(b for b in pre if b.line_no > opening.line_no)
    if extra is not None:
        emit(
            C,
            "opening-paragraph",
            f"line {extra.line_no}: only the opening paragraph may precede the "
            "first H2",
        )


def _before_first_h2(
    prose: Iterable[BodyLine],
) -> tuple[list[BodyLine], BodyLine | None]:
    """The non-stamp lines before the first H2, and that H2 if there is one."""
    pre: list[BodyLine] = []
    for b in prose:
        if b.in_stamp:
            continue
        if b.is_h2:
            return pre, b
        pre.append(b)
    return pre, None


def _first_extra_line(rest: Iterable[BodyLine]) -> BodyLine | None:
    """After the opening paragraph's first line, the first line not part of it.

    That is anything after a blank line, a fence, or a heading.
    """
    seen_blank = False
    for b in rest:
        if b.blank:
            seen_blank = True
        elif (
            seen_blank or b.kind is LineKind.FENCE or b.heading.kind is HeadingKind.ATX
        ):
            return b
    return None


# -- How you work ------------------------------------------------------------


def check_how_you_work(doc: AgentDoc, skeleton: Skeleton, emit: Emit) -> None:
    """'## How you work' is a numbered list and nothing else."""
    start = skeleton.positions.get(Row.HOW)
    if start is None:
        return
    lines = list(_section_content(b for b in doc.prose if b.line_no > start))
    if not lines:
        emit(C, "how-you-work", "'## How you work' holds no numbered list")
        return
    first, *rest = lines
    if not first.text.startswith("1. "):
        emit(
            C,
            "how-you-work",
            f"line {first.line_no}: '## How you work' must open with '1. ': "
            f"{first.text}",
        )
    for b in rest:
        if not NUMBERED_ITEM_RE.match(b.text) and not b.text.startswith("   "):
            emit(
                C,
                "how-you-work",
                f"line {b.line_no}: not a numbered item or a continuation indented "
                f"3+ spaces: {b.text}",
            )


def _section_content(rest: Iterable[BodyLine]) -> Iterator[BodyLine]:
    """A section's non-blank lines up to the next H2 or the stamp.

    Headings are skipped: heading-h3 and heading-level report them.
    """
    for b in rest:
        if b.in_stamp or b.is_h2:
            return
        if b.blank or (b.kind is LineKind.PROSE and b.text.startswith("#")):
            continue
        yield b


# -- Skeleton ----------------------------------------------------------------


def check_sections(skeleton: Skeleton, stier: int, emit: Emit) -> None:
    """Required, conditional and forbidden sections, by stamp tier."""
    pos = skeleton.positions
    for row, required, forbidden in SECTION_RULES:
        name = ROW_NAMES[row]
        if stier in required and row not in pos:
            emit(
                C,
                "heading-missing",
                (
                    f"missing '{name}'"
                    if required == ALL_TIERS
                    else f"stamp tier {stier} requires '{name}'"
                ),
            )
        if stier in forbidden and row in pos:
            emit(C, "heading-forbidden", f"stamp tier {stier} must not have '{name}'")


def check_order(skeleton: Skeleton, emit: Emit) -> None:
    """The fixed headings, and the stamp, in the skeleton's order."""
    pos = skeleton.positions
    last, last_row = 0, None
    for row in sorted(pos):
        if last_row is not None and pos[row] < last:
            emit(
                C,
                "heading-order",
                f"line {pos[row]}: {ROW_NAMES[row]} comes before "
                f"{ROW_NAMES[last_row]}; the order is Scope, How you work, Expert "
                "practice, Output, operating notes, Rollback, Approval gates",
            )
        else:
            last, last_row = pos[row], row


def check_domain_placement(skeleton: Skeleton, emit: Emit) -> None:
    """Domain H2s sit between How you work and Expert practice (or Output).

    They never follow the stamp.
    """
    pos = skeleton.positions
    closing = pos.get(Row.EXPERT, pos.get(Row.OUTPUT))
    bounds = [b for b in (closing, skeleton.stamp_at) if b is not None]
    lower, upper = pos.get(Row.HOW), min(bounds, default=None)
    for b in skeleton.domain:
        below = lower is None or b.line_no < lower
        above = upper is not None and b.line_no > upper
        if below or above:
            emit(
                C,
                "heading-order",
                f"line {b.line_no}: domain section '{b.text}' must sit "
                "between '## How you work' and '## Expert practice' "
                "(or '## Output')",
            )


# -- Headings and markup, line by line ----------------------------------------


def check_lines(doc: AgentDoc, skeleton: Skeleton, emit: Emit) -> None:
    """Markup and headings, line by line, stamp and code excluded."""
    prev: BodyLine | None = None
    for b in doc.prose:
        if b.in_stamp or b.kind is LineKind.FENCE:
            prev = None
            continue
        check_markup(b, prev, emit)
        prev = b
        check_heading(b, skeleton, emit)


def check_heading(b: BodyLine, skeleton: Skeleton, emit: Emit) -> None:
    """Heading syntax and level."""
    heading = b.heading
    if heading.kind is HeadingKind.RUN_IN:
        _check_run_in(b, emit)
    elif heading.kind is HeadingKind.NONE:
        return
    elif heading.level == 1 or heading.level >= 4:
        emit(
            C,
            "heading-level",
            f"line {b.line_no}: H{heading.level} is banned; use H2 or H3: {b.text}",
        )
    elif heading.level == 2:
        _check_h2(b, skeleton, emit)
    else:
        _check_h3(b, emit)


def _well_spaced(text: str) -> bool:
    """Heading text after the hashes: exactly one space, no trailing space."""
    return bool(HEADING_TEXT_RE.match(text)) and not text.endswith((" ", "\t"))


def _check_run_in(b: BodyLine, emit: Emit) -> None:
    """'##Text': a near miss of a fixed heading, or a format error."""
    level = b.heading.level
    near = FIXED_BY_NORM.get(norm(b.heading.text)) if level == 2 else None
    if near:
        emit(
            C,
            "heading-near-miss",
            f"line {b.line_no}: '{b.text}' is not exactly '{near}'",
        )
    else:
        emit(
            C,
            "heading-format",
            f"line {b.line_no}: no space after the hashes: {b.text}",
        )


def _check_h2(b: BodyLine, skeleton: Skeleton, emit: Emit) -> None:
    """A fixed heading exactly as the skeleton spells it, once; or a domain one."""
    row = FIXED_HEADINGS.get(b.text)
    near = FIXED_BY_NORM.get(norm(b.heading.text))
    if row is Row.STAMP:
        emit(
            C,
            "heading-operating-notes",
            f"line {b.line_no}: '## Operating notes' outside the stamped block",
        )
    elif row is not None:
        if skeleton.rows[row][0].line_no != b.line_no:
            emit(
                C,
                "heading-duplicate",
                f"line {b.line_no}: '{b.text}' appears more than once",
            )
    elif near:
        emit(
            C,
            "heading-near-miss",
            f"line {b.line_no}: '{b.text}' is not exactly '{near}'",
        )
    elif not _well_spaced(b.heading.text):
        emit(
            C,
            "heading-format",
            f"line {b.line_no}: use exactly one space after '##' and no "
            f"trailing space: '{b.text}'",
        )


def _check_h3(b: BodyLine, emit: Emit) -> None:
    """Spacing, and no H3 under How you work."""
    if not _well_spaced(b.heading.text):
        emit(
            C,
            "heading-format",
            f"line {b.line_no}: use exactly one space after '###' and no "
            f"trailing space: '{b.text}'",
        )
    if b.h2 == "## How you work":
        emit(
            C,
            "heading-h3",
            f"line {b.line_no}: no H3 under '## How you work': {b.text}",
        )


def check_markup(b: BodyLine, prev: BodyLine | None, emit: Emit) -> None:
    """Setext headings, bold-only lines, HTML comments, indented headings."""
    s = b.text
    if SETEXT_RE.match(s) and _can_be_setext_title(prev):
        emit(
            C,
            "heading-setext",
            f"line {b.line_no}: setext heading underline; use an ATX heading",
        )
    if BOLD_ONLY_RE.match(s):
        emit(
            C,
            "bold-only-line",
            f"line {b.line_no}: a line of only bold text; use an H3: {s}",
        )
    if "<!--" in s and "<!-- TEMPLATE:" not in s:
        emit(
            C,
            "html-comment",
            f"line {b.line_no}: the only HTML comments allowed are the stamp markers",
        )
    if (
        INDENTED_HASH_RE.match(s)
        and parse_heading(s.strip(" \t")).kind is HeadingKind.ATX
    ):
        emit(C, "heading-format", f"line {b.line_no}: indented heading: {s}")


def _can_be_setext_title(prev: BodyLine | None) -> bool:
    """Whether a --- or === under prev makes prev a setext heading."""
    if prev is None or prev.blank:
        return False
    return prev.heading.kind is not HeadingKind.ATX and not LIST_ITEM_RE.match(
        prev.text
    )
