"""Behaviour of scripts/lint_model.py: the parsed form every rule reads."""

# Test names say what each test checks, and `== ()` shows the unexpected
# lines in pytest's failure diff where `not ...` would not.
# pylint: disable=missing-function-docstring
# pylint: disable=use-implicit-booleaness-not-comparison

from __future__ import annotations

import pytest
from builders import lint, make_agent, rules
from lint_model import (
    NOT_A_HEADING,
    Heading,
    HeadingKind,
    LineKind,
    Row,
    StampMarkers,
    index_skeleton,
    parse_doc,
    parse_heading,
)


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("## Scope", Heading(HeadingKind.ATX, 2, " Scope")),
        ("##\tScope", Heading(HeadingKind.ATX, 2, "\tScope")),
        ("##", Heading(HeadingKind.ATX, 2, "")),
        ("### Detail", Heading(HeadingKind.ATX, 3, " Detail")),
        ("##Scope", Heading(HeadingKind.RUN_IN, 2, "Scope")),
        ("#hashtag", NOT_A_HEADING),
        ("text", NOT_A_HEADING),
        (" ## indented", NOT_A_HEADING),
    ],
)
def test_parse_heading(line: str, expected: Heading) -> None:
    assert parse_heading(line) == expected


def test_parse_doc_classifies_lines_and_carries_context() -> None:
    doc = parse_doc(
        "---\nname: x\n---\nYou are a x.\n## Rollback\n### Terraform\n"
        "````bash\n## not a heading\n````\nafter\n"
    )
    kinds = [(b.line_no, b.kind) for b in doc.body]
    assert kinds == [
        (4, LineKind.PROSE),
        (5, LineKind.PROSE),
        (6, LineKind.PROSE),
        (7, LineKind.FENCE),
        (8, LineKind.CODE),
        (9, LineKind.CODE),
        (10, LineKind.PROSE),
    ]
    code = doc.body[4]
    assert code.heading == NOT_A_HEADING
    assert (code.section, code.h2) == ("### Terraform", "## Rollback")
    assert [b.line_no for b in doc.prose] == [4, 5, 6, 7, 10]


def test_parse_doc_without_closed_frontmatter_has_no_body() -> None:
    assert parse_doc("---\nname: x\n").body == ()
    assert parse_doc("no frontmatter\n").frontmatter is None


def test_stamp_lines_are_marked_and_do_not_move_the_h2() -> None:
    doc = parse_doc(make_agent(3))
    stamp = [b for b in doc.body if b.in_stamp]
    assert stamp[0].text.startswith("<!-- BEGIN GENERATED")
    assert stamp[-1].text == "<!-- END GENERATED: operating-notes -->"
    assert {b.h2 for b in stamp} == {"## Output"}
    assert doc.stamp_markers().span == (stamp[0].line_no, stamp[-1].line_no)


def test_index_skeleton() -> None:
    text = make_agent(3).replace(
        "## Sample domain", "## Sample domain\n\n## scope\n\n## Scope"
    )
    doc = parse_doc(text)
    begin = doc.stamp_markers().begins[0]
    skeleton = index_skeleton(doc, begin)
    assert [b.text for b in skeleton.rows[Row.SCOPE]] == ["## Scope", "## Scope"]
    assert [b.text for b in skeleton.domain] == ["## Sample domain"]
    assert skeleton.positions[Row.STAMP] == begin
    assert skeleton.positions[Row.SCOPE] == skeleton.rows[Row.SCOPE][0].line_no


def test_every_h2_check_agrees_on_a_tab_separated_heading() -> None:
    # "##\tX" is an ATX H2. Before lint_model.py, the How-you-work walk used
    # startswith("## ") and read past it into the next section.
    text = make_agent().replace("## Sample domain", "##\tSample domain")
    assert rules(lint(text)) == {"heading-format"}


@pytest.mark.parametrize(
    ("begins", "ends", "span"),
    [
        ((3,), (5,), (3, 5)),
        ((5,), (3,), None),
        ((3, 4), (5,), None),
        ((3,), (), None),
    ],
)
def test_stamp_markers_span(
    begins: tuple[int, ...], ends: tuple[int, ...], span: tuple[int, int] | None
) -> None:
    markers = StampMarkers(begins, ends)
    assert markers.present
    assert markers.span == span


def test_h2_lookups() -> None:
    doc = parse_doc(make_agent())
    output = doc.h2_line("## Output")
    assert output is not None
    after = doc.next_h2(output)
    assert after is not None and doc.lines[after - 1] == "## Operating notes"
    assert doc.next_h2(after) is None
    assert doc.h2_line("## Nowhere") is None
