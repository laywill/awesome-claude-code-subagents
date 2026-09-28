"""The parsed form of an agent file that the content lint and the stamper read.

parse_doc() walks a file once and returns an immutable AgentDoc: its lines,
its frontmatter, and each body line classified (prose, fence opening or
code) with its heading, whether it sits in the stamped block, and the
headings it sits under. index_skeleton() derives the fixed and domain H2s
from that. Rules in scripts/lint_*.py are functions over these types and
never re-parse text, so there is one definition of a heading, an H2, a fence
and a stamp marker.

Standard library only: CI runs it with the runner's system Python.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum
from typing import NamedTuple

from agent_file import (
    BEGIN_MARK,
    END_MARK,
    Frontmatter,
    closes_fence,
    fence_open,
    parse_frontmatter,
    split_lines,
)


class Severity(StrEnum):
    """How catalog_lint.py treats a finding. The values are what it prints."""

    RATCHETED = "C"  # FAIL in an enforced category, WARN elsewhere
    FAIL = "F"  # always FAIL: a stamped block that is malformed or drifted
    WARN = "W"  # always WARN: a heuristic


# How rules report a finding: emit(severity, rule, message).
Emit = Callable[[Severity, str, str], None]


# -- Headings ----------------------------------------------------------------


class HeadingKind(Enum):
    """What a line's leading hashes make it."""

    NONE = "none"  # not a heading
    ATX = "atx"  # hashes, then a space, tab or end of line
    RUN_IN = "run-in"  # "##Text": two or more hashes run into text


class Heading(NamedTuple):
    """A line classified as an ATX heading, or not."""

    kind: HeadingKind
    level: int
    text: str  # everything after the hashes, spacing included


NOT_A_HEADING = Heading(HeadingKind.NONE, 0, "")


def parse_heading(line: str) -> Heading:
    """Classify a line, unindented, as an ATX heading."""
    if not line.startswith("#"):
        return NOT_A_HEADING
    level = len(line) - len(line.lstrip("#"))
    rest = line[level:]
    if rest == "" or rest[0] in " \t":
        return Heading(HeadingKind.ATX, level, rest)
    if level >= 2:
        return Heading(HeadingKind.RUN_IN, level, rest)
    return NOT_A_HEADING


def norm(text: str) -> str:
    """Lower-case and collapse whitespace, for near-miss heading matching."""
    return re.sub(r"[ \t]+", " ", text.lower()).strip(" \t")


# -- Body lines --------------------------------------------------------------


class LineKind(Enum):
    """Where a body line sits relative to fenced code."""

    PROSE = "prose"
    FENCE = "fence"  # a fence's opening line; it stands in for the block
    CODE = "code"  # inside a fenced block, closing fence included


@dataclass(frozen=True)
class BodyLine:
    """One body line, classified in context."""

    text: str
    line_no: int  # 1-based, in the whole file
    kind: LineKind
    heading: Heading  # NOT_A_HEADING unless kind is PROSE
    in_stamp: bool  # between the BEGIN and END markers, both included
    section: str  # the nearest heading line above, any level, stamp included
    h2: str  # the nearest H2 line above, or this one, outside the stamp

    @property
    def is_h2(self) -> bool:
        """An ATX H2 in prose. Every section boundary uses this."""
        return self.heading.kind is HeadingKind.ATX and self.heading.level == 2

    @property
    def blank(self) -> bool:
        """Only spaces and tabs."""
        return self.text.strip(" \t") == ""


@dataclass(frozen=True)
class AgentDoc:
    """An agent file as the lint and the stamper see it."""

    lines: tuple[str, ...]
    frontmatter: Frontmatter | None
    body: tuple[BodyLine, ...]  # every line after the frontmatter

    @property
    def prose(self) -> tuple[BodyLine, ...]:
        """The body with code dropped: prose lines and each fence's opening."""
        return tuple(b for b in self.body if b.kind is not LineKind.CODE)

    def stamp_markers(self) -> StampMarkers:
        """The BEGIN and END markers in prose."""
        prose = [b for b in self.body if b.kind is LineKind.PROSE]
        return StampMarkers(
            tuple(b.line_no for b in prose if b.text.startswith(BEGIN_MARK)),
            tuple(b.line_no for b in prose if b.text == END_MARK),
        )

    def h2_line(self, text: str) -> int | None:
        """The line of the first H2 that reads exactly text."""
        return next((b.line_no for b in self.body if b.is_h2 and b.text == text), None)

    def next_h2(self, after: int) -> int | None:
        """The line of the first H2 below line after."""
        return next(
            (b.line_no for b in self.body if b.line_no > after and b.is_h2), None
        )


@dataclass(frozen=True)
class StampMarkers:
    """Line numbers of the operating-notes markers, however many there are."""

    begins: tuple[int, ...]
    ends: tuple[int, ...]

    @property
    def present(self) -> bool:
        """Any marker at all."""
        return bool(self.begins or self.ends)

    @property
    def span(self) -> tuple[int, int] | None:
        """(BEGIN, END) when there is exactly one of each, in that order."""
        if len(self.begins) != 1 or len(self.ends) != 1:
            return None
        begin, end = self.begins[0], self.ends[0]
        return (begin, end) if begin < end else None


@dataclass
class _Cursor:
    """Context carried down the body while parse_doc() walks it."""

    fence: tuple[str, int] | None = None
    in_stamp: bool = False
    section: str = ""
    h2: str = ""

    def classify(self, line: str, line_no: int) -> BodyLine:
        """The BodyLine for line, advancing the context past it."""
        stripped = line.lstrip(" \t")
        if self.fence:
            if closes_fence(stripped, *self.fence):
                self.fence = None
            return self._line(line, line_no, LineKind.CODE, NOT_A_HEADING)
        self.fence = fence_open(stripped)
        if self.fence:
            return self._line(line, line_no, LineKind.FENCE, NOT_A_HEADING)

        self.in_stamp = self.in_stamp or line.startswith(BEGIN_MARK)
        heading = parse_heading(line)
        if heading.kind is HeadingKind.ATX:
            self.section = line
            if heading.level == 2 and not self.in_stamp:
                self.h2 = line
        parsed = self._line(line, line_no, LineKind.PROSE, heading)
        self.in_stamp = self.in_stamp and line != END_MARK
        return parsed

    def _line(
        self, line: str, line_no: int, kind: LineKind, heading: Heading
    ) -> BodyLine:
        return BodyLine(
            line, line_no, kind, heading, self.in_stamp, self.section, self.h2
        )


def parse_doc(text: str) -> AgentDoc:
    """Parse an agent file's text. A file with no closed frontmatter has no body."""
    return parse_lines(split_lines(text))


def parse_lines(lines: list[str]) -> AgentDoc:
    """parse_doc() for text already split with agent_file.split_lines()."""
    fm = parse_frontmatter(lines)
    start = fm.body_start if fm and fm.closed else len(lines)
    cursor = _Cursor()
    body = tuple(
        cursor.classify(line, no)
        for no, line in enumerate(lines[start:], start=start + 1)
    )
    return AgentDoc(tuple(lines), fm, body)


# -- The body skeleton ---------------------------------------------------------


class Row(IntEnum):
    """Fixed headings by their row in CLAUDE.md's Body skeleton.

    Row 3 is the domain sections, which have no fixed heading.
    """

    SCOPE = 1
    HOW = 2
    EXPERT = 4
    OUTPUT = 5
    STAMP = 6
    ROLLBACK = 7
    GATES = 8


FIXED_HEADINGS: Mapping[str, Row] = {
    "## Scope": Row.SCOPE,
    "## How you work": Row.HOW,
    "## Expert practice": Row.EXPERT,
    "## Output": Row.OUTPUT,
    "## Operating notes": Row.STAMP,
    "## Rollback": Row.ROLLBACK,
    "## Approval gates": Row.GATES,
}
ROW_NAMES: Mapping[Row, str] = {
    **{row: heading for heading, row in FIXED_HEADINGS.items()},
    Row.STAMP: "the operating-notes stamp",
}
# Fixed headings keyed by norm() of their text, to spot near misses.
FIXED_BY_NORM: Mapping[str, str] = {norm(h[3:]): h for h in FIXED_HEADINGS}


@dataclass(frozen=True)
class Skeleton:
    """The H2s outside the stamp, sorted into fixed rows and domain sections."""

    rows: Mapping[Row, tuple[BodyLine, ...]]  # every occurrence, in order
    domain: tuple[BodyLine, ...]
    near_misses: tuple[tuple[BodyLine, str], ...]  # (line, the fixed heading)
    stamp_at: int | None = None  # the BEGIN marker's line, when well-formed

    @property
    def positions(self) -> dict[Row, int]:
        """The line of each row's first heading, and of a well-formed stamp.

        "## Operating notes" written by hand doesn't place the stamp row.
        """
        pos: dict[Row, int] = {
            r: lines[0].line_no for r, lines in self.rows.items() if r != Row.STAMP
        }
        if self.stamp_at is not None:
            pos[Row.STAMP] = self.stamp_at
        return pos


def index_skeleton(doc: AgentDoc, stamp_at: int | None) -> Skeleton:
    """Sort the H2s outside the stamp into the skeleton's rows."""
    rows: dict[Row, list[BodyLine]] = {}
    domain: list[BodyLine] = []
    near: list[tuple[BodyLine, str]] = []
    for b in doc.body:
        if not b.is_h2 or b.in_stamp:
            continue
        row = FIXED_HEADINGS.get(b.text)
        if row is not None:
            rows.setdefault(row, []).append(b)
        elif norm(b.heading.text) in FIXED_BY_NORM:
            near.append((b, FIXED_BY_NORM[norm(b.heading.text)]))
        else:
            domain.append(b)
    return Skeleton(
        {r: tuple(lines) for r, lines in rows.items()},
        tuple(domain),
        tuple(near),
        stamp_at,
    )
