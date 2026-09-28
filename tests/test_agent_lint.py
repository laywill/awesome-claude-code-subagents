"""Behaviour of scripts/agent_lint.py, one rule at a time."""

# Test names say what each test checks, and `== []` shows the unexpected
# findings in pytest's failure diff where `not ...` would not.
# pylint: disable=missing-function-docstring
# pylint: disable=use-implicit-booleaness-not-comparison

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import agent_file
import agent_lint
import pytest
from agent_file import Allowlist
from builders import TEMPLATES, lint, make_agent, rules, stamp_block
from lint_model import Severity

# -- Baseline -----------------------------------------------------------------


@pytest.mark.parametrize("tier", [1, 2, 3, 4, 5])
def test_valid_agent_is_clean(tier: int) -> None:
    assert lint(make_agent(tier), tier) == []


def test_crlf_file_reads_like_lf() -> None:
    assert lint(make_agent(4).replace("\n", "\r\n"), 4) == []


def test_lone_cr_is_not_a_line_break() -> None:
    # How git and editorconfig-checker see it: one line, so no closing fence.
    text = make_agent().replace("\n", "\r")
    assert rules(lint(text)) == set()  # no opening "---" line either


def test_file_without_frontmatter_only_gets_whole_file_checks() -> None:
    text = "# Title\n\nWhen invoked:\n"
    assert rules(lint(text)) == {"banned-when-invoked"}


def test_file_outside_a_tiered_category_gets_no_tier_checks() -> None:
    findings = agent_lint.lint_file(
        "categories/99-unknown/x.md", "---\nname: x\n---\n", TEMPLATES, Allowlist()
    )
    assert findings == []


# -- Frontmatter ----------------------------------------------------------------


def test_unclosed_frontmatter() -> None:
    assert rules(lint("---\nname: sample-agent\n")) == {"frontmatter"}


def test_duplicate_key() -> None:
    text = make_agent().replace("model: sonnet", "model: sonnet\nmodel: sonnet")
    assert rules(lint(text)) == {"frontmatter-duplicate-key"}


@pytest.mark.parametrize(
    ("key", "wording"),
    [
        ("permissionMode", "forbidden"),
        ("isolation", "doesn't use"),
        ("maxturns", "not a recognised key"),
    ],
)
def test_frontmatter_keys(key: str, wording: str) -> None:
    fields: dict[str, Any] = {key: "x"}
    findings = lint(make_agent(**fields))
    assert [f.rule for f in findings] == ["frontmatter-key"]
    assert wording in findings[0].message


def test_quoted_values_are_unquoted() -> None:
    assert lint(make_agent(model="'sonnet'", color='"green"')) == []


@pytest.mark.parametrize("name", ["Sample", "sample_agent", "sample-", "-sample", ""])
def test_name_format(name: str) -> None:
    assert "name-format" in rules(lint(make_agent(name=name)))


def test_description_limit_counts_characters_not_bytes() -> None:
    at_limit = "é" * 250
    assert lint(make_agent(description=at_limit)) == []
    findings = lint(make_agent(description=at_limit + "e"))
    assert [f.rule for f in findings] == ["description-length"]
    assert "251 characters" in findings[0].message


@pytest.mark.parametrize(
    "description",
    [
        "|",
        ">-",
        '"First line.\\nSecond line."',
        "Starts here\n  and continues",
    ],
)
def test_multiline_description(description: str) -> None:
    assert rules(lint(make_agent(description=description))) == {"description-format"}


def test_description_example_block() -> None:
    assert rules(lint(make_agent(description="Do it. <example>x</example>"))) == {
        "description-format"
    }


def test_comment_after_description_is_not_a_continuation() -> None:
    text = make_agent().replace("model:", "# note\nmodel:")
    assert lint(text) == []


@pytest.mark.parametrize("model", ["fable", "inherit", "claude-sonnet-5", ""])
def test_model_value(model: str) -> None:
    assert rules(lint(make_agent(model=model))) == {"model-value"}


@pytest.mark.parametrize(
    ("tools", "wording"),
    [
        ("Read, Bash(git *)", "specifier"),
        ("Read, mcp__github__get", "specifier or MCP"),
        ("Read, Grepp", "unrecognised"),
    ],
)
def test_tool_names(tools: str, wording: str) -> None:
    findings = [f for f in lint(make_agent(tools=tools)) if f.rule == "tools-format"]
    assert len(findings) == 1 and wording in findings[0].message


def test_tool_in_both_lists() -> None:
    text = make_agent(tools="Read, Grep, Glob, Write")
    assert "tools-overlap" in rules(lint(text))


@pytest.mark.parametrize("tier", [1, 2, 3, 4, 5])
def test_color_follows_category_tier(tier: int) -> None:
    findings = lint(make_agent(tier, color="blue"), tier)
    assert rules(findings) == {"color-tier"}
    findings = lint(make_agent(tier, color=None), tier)
    assert "'<absent>'" in findings[0].message


def test_tier1_must_disallow_bash() -> None:
    text = make_agent(disallowedTools="Write, Edit, NotebookEdit")
    assert rules(lint(text)) == {"tier1-bash"}


def test_tier1_bash_needs_allowlist_entry() -> None:
    text = make_agent(tools="Read, Grep, Glob, Bash", disallowedTools="Write, Edit")
    # Bash is write-capable, so the file also takes its category's stamp tier.
    assert "tier1-bash" in rules(lint(text))
    allow = Allowlist(exemptions={("sample-agent", "tier1-bash")})
    assert "tier1-bash" not in rules(lint(text, allow=allow))


@pytest.mark.parametrize(
    ("tier", "overrides", "expected"),
    [
        (1, {"effort": "medium"}, "not allowed"),
        (1, {"model": "opus", "effort": "high"}, "absent on opus"),
        (1, {"model": "haiku", "effort": "high"}, "absent on haiku"),
        (4, {"effort": None}, "require effort: high"),
        (1, {"effort": "high"}, "sonnet-instead-of-opus"),
    ],
)
def test_effort(tier: int, overrides: dict[str, Any], expected: str) -> None:
    messages = [f.message for f in lint(make_agent(tier, **overrides), tier)]
    assert any(expected in m for m in messages), messages


def test_effort_allowlisted_on_low_tier() -> None:
    allow = Allowlist(exemptions={("sample-agent", "sonnet-instead-of-opus")})
    assert lint(make_agent(effort="high"), allow=allow) == []


@pytest.mark.parametrize(
    ("tier", "max_turns", "expected"),
    [
        (4, "abc", "not a positive integer"),
        (4, "025", "not a positive integer"),
        (2, "10", "must not set maxTurns"),
        (4, "25", "requires maxTurns: 40"),
        (5, None, "requires maxTurns: 25, got ''"),
    ],
)
def test_max_turns(tier: int, max_turns: str | None, expected: str) -> None:
    messages = [f.message for f in lint(make_agent(tier, maxTurns=max_turns), tier)]
    assert any(expected in m for m in messages), messages


# -- Stamp ------------------------------------------------------------------------


def test_stamp_missing() -> None:
    text = make_agent().replace(stamp_block(1), "")
    assert rules(lint(text)) == {"stamp-missing"}


def test_stamp_drift_always_fails() -> None:
    text = make_agent().replace("You are advisory", "You are advisory, mostly")
    findings = lint(text)
    assert [(f.severity, f.rule) for f in findings] == [(Severity.FAIL, "stamp-drift")]


def test_stamp_tier_follows_tools() -> None:
    # A tier 5 agent with no write-capable tool takes the tier 1 notes.
    text = make_agent(5, stier=1, tools="Read, Grep, Glob")
    assert lint(text, 5) == []
    # The tier 1 notes also forbid the ## Rollback the tier 5 skeleton holds.
    findings = lint(make_agent(5, tools="Read, Grep, Glob"), 5)
    assert rules(findings) == {"stamp-drift", "heading-forbidden"}


def test_stamp_tier_allowlist_override() -> None:
    allow = Allowlist(tier_overrides={"sample-agent": 5})
    assert lint(make_agent(2, stier=5), 2, allow=allow) == []
    assert "stamp-drift" in rules(lint(make_agent(2), 2, allow=allow))


@pytest.mark.parametrize(
    "mangle",
    [
        lambda s: s + "\n" + stamp_block(1).splitlines()[0],  # two BEGIN
        lambda s: s.replace(stamp_block(1).splitlines()[-1], ""),  # no END
        lambda s: agent_file.END_MARK + "\n\n" + s.replace(agent_file.END_MARK, ""),
    ],
)
def test_stamp_malformed_always_fails(mangle: Callable[[str], str]) -> None:
    body_at = make_agent().index("You are")
    text = make_agent()
    text = text[:body_at] + mangle(text[body_at:])
    assert (Severity.FAIL, "stamp-malformed") in {
        (f.severity, f.rule) for f in lint(text)
    }


def test_stamp_markers_inside_code_are_ignored() -> None:
    text = make_agent().replace(
        "Domain detail.", "Domain detail.\n\n```markdown\n" + stamp_block(1) + "\n```"
    )
    assert lint(text) == []


def test_text_between_stamp_and_next_h2() -> None:
    text = make_agent(3).replace("## Rollback", "Stray text.\n\n## Rollback")
    assert rules(lint(text, 3)) == {"stamp-position"}


# -- Body skeleton ---------------------------------------------------------------


def test_opening_must_be_you_are() -> None:
    text = make_agent().replace("You are a sample reviewer.", "This agent reviews.")
    assert rules(lint(text)) == {"opening-paragraph"}


def test_opening_you_are_an() -> None:
    assert lint(make_agent().replace("You are a sample", "You are an example")) == []


def test_only_one_paragraph_before_first_h2() -> None:
    text = make_agent().replace("reviewer.", "reviewer.\n\nSecond paragraph.\n\nThird.")
    findings = lint(text)
    assert [f.rule for f in findings] == ["opening-paragraph"]  # reported once


def test_heading_before_first_h2() -> None:
    text = make_agent().replace("reviewer.", "reviewer.\n### Aside")
    assert "opening-paragraph" in rules(lint(text))


def test_no_opening_paragraph() -> None:
    text = make_agent().replace("You are a sample reviewer.\n\n", "")
    findings = lint(text)
    assert [f.rule for f in findings] == ["opening-paragraph"]
    assert "no opening" in findings[0].message


def test_empty_body() -> None:
    assert "opening-paragraph" in rules(lint("---\nname: sample-agent\n---\n\n\n"))


@pytest.mark.parametrize(
    ("tier", "heading", "rule"),
    [
        (1, "## Scope", "heading-missing"),
        (1, "## How you work", "heading-missing"),
        (1, "## Output", "heading-missing"),
        (2, "## Expert practice", "heading-missing"),
        (3, "## Rollback", "heading-missing"),
    ],
)
def test_required_headings(tier: int, heading: str, rule: str) -> None:
    text = make_agent(tier).replace(heading + "\n", "## Renamed\n")
    assert rule in rules(lint(text, tier))


@pytest.mark.parametrize("heading", ["## Rollback", "## Approval gates"])
def test_tier1_forbids_rollback_and_gates(heading: str) -> None:
    text = make_agent() + f"\n{heading}\n\nText.\n"
    assert "heading-forbidden" in rules(lint(text))


def test_approval_gates_allowed_above_tier1() -> None:
    assert lint(make_agent(4) + "\n## Approval gates\n\nDBA sign-off.\n", 4) == []


def test_section_order() -> None:
    text = make_agent().replace("## Scope\n\nSample scope.\n\n", "")
    text = text.replace("## Output", "## Scope\n\nSample scope.\n\n## Output")
    findings = [f for f in lint(text) if f.rule == "heading-order"]
    assert findings and "comes before" in findings[0].message


def test_domain_section_after_output() -> None:
    text = make_agent().replace("## Output", "## Late domain\n\nText.\n\n## Output")
    text = text.replace("## Sample domain\n\nDomain detail.\n\n", "")
    assert lint(text) == []
    text = make_agent() + "\n## Trailing domain\n\nText.\n"
    assert rules(lint(text)) == {"heading-order"}


def test_domain_section_before_how_you_work() -> None:
    text = make_agent().replace("## Scope", "## Early\n\nText.\n\n## Scope")
    assert "heading-order" in rules(lint(text))


def test_duplicate_fixed_heading() -> None:
    text = make_agent().replace("## Sample domain", "## Scope")
    assert "heading-duplicate" in rules(lint(text))


def test_operating_notes_heading_outside_stamp() -> None:
    text = make_agent().replace("## Sample domain", "## Operating notes")
    assert "heading-operating-notes" in rules(lint(text))


@pytest.mark.parametrize(
    ("heading", "rule"),
    [
        ("## scope", "heading-near-miss"),
        ("##  Scope", "heading-near-miss"),
        ("##Scope", "heading-near-miss"),
        ("##Sample domain", "heading-format"),
        ("## Sample domain ", "heading-format"),
        ("#  Sample domain", "heading-level"),
        ("#### Sample domain", "heading-level"),
    ],
)
def test_heading_format(heading: str, rule: str) -> None:
    text = make_agent().replace(
        "## Scope" if "cope" in heading else "## Sample domain", heading
    )
    assert rule in rules(lint(text))


def test_h3_format_and_placement() -> None:
    text = make_agent().replace("Domain detail.", "### Detail \n\nText.")
    assert rules(lint(text)) == {"heading-format"}
    text = make_agent().replace("2. Report.", "2. Report.\n\n### Step detail")
    assert rules(lint(text)) == {"heading-h3"}


# -- How you work ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("how", "wording"),
    [
        ("Prose first.\n1. Read.", "must open with '1. '"),
        ("1. Read.\n- bullet", "not a numbered item"),
        ("1. Read.\n  two-space continuation", "not a numbered item"),
        ("", "holds no numbered list"),
    ],
)
def test_how_you_work_is_a_numbered_list(how: str, wording: str) -> None:
    text = make_agent().replace("1. Read.\n2. Report.\n   Continued.", how)
    messages = [f.message for f in lint(text) if f.rule == "how-you-work"]
    assert len(messages) == 1 and wording in messages[0]


# -- Markup ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("line", "rule"),
    [
        ("Setext\n===", "heading-setext"),
        ("Setext\n  ---", "heading-setext"),
        ("**Bold only**", "bold-only-line"),
        ("**Bold label**:", "bold-only-line"),
        ("<!-- note -->", "html-comment"),
        ("  ## Indented", "heading-format"),
    ],
)
def test_markup(line: str, rule: str) -> None:
    text = make_agent().replace("Domain detail.", line)
    assert rule in rules(lint(text))


@pytest.mark.parametrize(
    "line",
    [
        "- item\n---",  # a thematic break after a list, not a setext underline
        "Text with **bold** inside.",
        "    # indented four spaces is code, not a heading",
    ],
)
def test_markup_false_positives(line: str) -> None:
    assert lint(make_agent().replace("Domain detail.", line)) == []


def test_code_fences_hide_markup() -> None:
    code = "~~~~\n# comment\n**bold**\n<!-- x -->\n```\nstill code\n~~~~"
    assert lint(make_agent().replace("Domain detail.", code)) == []


# -- Banned content --------------------------------------------------------------------


@pytest.mark.parametrize(
    ("line", "rule"),
    [
        ("# TEMPLATE: fill in", "template-leftover"),
        ("See <!-- TEMPLATE: x -->", "template-leftover"),
        ("When invoked:", "banned-when-invoked"),
        ("On invocation: do it", "banned-when-invoked"),
        ("touch EMERGENCY_STOP", "banned-emergency-stop"),
        ("Open a Change Ticket first.", "banned-approval-gate"),
        ("read -p 'Continue?'", "banned-approval-gate"),
        ("**Environment note:** local", "banned-environment-preamble"),
    ],
)
def test_banned_content(line: str, rule: str) -> None:
    assert rule in rules(lint(make_agent().replace("Domain detail.", line)))


def test_banned_content_in_frontmatter_and_code() -> None:
    text = make_agent(description="When invoked: review.")
    assert "banned-when-invoked" in rules(lint(text))
    text = make_agent().replace("Domain detail.", "```\nWhen invoked:\n```")
    assert "banned-when-invoked" in rules(lint(text))


@pytest.mark.parametrize(
    "heading",
    [
        "## Security Safeguards",
        "### Emergency Stop Procedures",
        "## Input validation",
        "## Environment Adaptability (all)",
        "## Approval Gates",
    ],
)
def test_retired_headings(heading: str) -> None:
    text = make_agent(4).replace("## Sample domain", heading)
    assert "banned-heading" in rules(lint(text, 4))


def test_auto_approve_only_banned_under_rollback() -> None:
    apply = "terraform apply -auto-approve"
    text = make_agent(4).replace("git revert HEAD", apply)
    findings = [f for f in lint(text, 4) if f.rule == "banned-auto-approve"]
    assert len(findings) == 1
    assert lint(make_agent(4).replace("Domain detail.", apply), 4) == []


@pytest.mark.parametrize(
    "line",
    [
        "Reach 95% coverage.",
        "Accuracy of 99.",
        "Latency: <= 200 in tests.",
        "Respond in < 5 min always.",
    ],
)
def test_invented_metric_only_warns(line: str) -> None:
    findings = lint(make_agent().replace("Domain detail.", line))
    assert [(f.severity, f.rule) for f in findings] == [
        (Severity.WARN, "metric-invented")
    ]


# -- Shared parsing ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "tier"),
    [
        ("categories/01-a/x.md", 1),
        ("categories/06-a/x.md", 1),
        ("categories/07-a/x.md", 2),
        ("categories/13-a/x.md", 2),
        ("categories/14-a/x.md", 3),
        ("categories/17-a/x.md", 3),
        ("categories/18-a/x.md", 4),
        ("categories/21-a/x.md", 4),
        ("categories/22-a/x.md", 5),
        ("categories/24-a/x.md", 5),
        ("/abs/repo/categories/24-a/x.md", 5),
        ("categories/00-a/x.md", None),
        ("categories/25-a/x.md", None),
        ("categories/22-a/sub/x.md", None),
        ("other/22-a/x.md", None),
    ],
)
def test_category_tier(path: str, tier: int | None) -> None:
    assert agent_file.category_tier(path) == tier


def test_split_lines() -> None:
    assert agent_file.split_lines("a\r\nb\n") == ["a", "b"]
    assert agent_file.split_lines("a\rb") == ["a\rb"]
    assert agent_file.split_lines("a\n\n") == ["a", ""]
    assert agent_file.split_lines("") == []


def test_allowlist_parse() -> None:
    allow = Allowlist.parse(
        "# header: comment\nchaos-engineer: tier=5 # why\nx-agent: tier1-bash # why\n"
    )
    assert allow.tier_overrides == {"chaos-engineer": 5}
    assert allow.allows("x-agent", "tier1-bash")
    assert not allow.allows("header", "comment")
