"""Behaviour of scripts/stamp_sections.py."""

# Test names say what each test checks, and `== []` shows the unexpected
# findings in pytest's failure diff where `not ...` would not.
# pytest isn't installed where MegaLinter runs pylint; the pytest job fails
# on an import that is really missing.
# pylint: disable=import-error,missing-function-docstring
# pylint: disable=use-implicit-booleaness-not-comparison

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import stamp_sections
from agent_file import Allowlist, split_lines
from builders import ROOT, TEMPLATES, lint, make_agent, stamp_block


def unstamped(tier: int = 1, **overrides: Any) -> str:
    """make_agent() with its stamp removed, as a pre-stamp file looks."""
    return (
        make_agent(tier, **overrides)
        .replace(stamp_block(tier) + "\n\n", "")
        .replace("\n\n" + stamp_block(tier), "")
    )


def stamped(text: str, tier: int) -> str:
    """Run stamp() over text and join the result as the file would be written."""
    return "".join(
        line + "\n" for line in stamp_sections.stamp(split_lines(text), TEMPLATES[tier])
    )


@pytest.mark.parametrize("tier", [1, 3, 5])
def test_insert_restores_the_valid_file(tier: int) -> None:
    # Tier 1 ends at the stamp; tiers 3 and 5 put it before ## Rollback.
    assert stamped(unstamped(tier), tier) == make_agent(tier)


def test_insert_collapses_blank_lines_after_output() -> None:
    text = unstamped().replace("Findings.\n", "Findings.\n\n\n\n")
    assert stamped(text, 1) == make_agent()


def test_refresh_replaces_a_drifted_block_in_place() -> None:
    drifted = make_agent(3).replace("Undo steps are under Rollback.", "Old wording.")
    assert stamped(drifted, 3) == make_agent(3)


def test_restamp_is_idempotent() -> None:
    once = stamped(unstamped(4), 4)
    assert stamped(once, 4) == once


def test_markers_and_output_inside_code_are_ignored() -> None:
    code = "```markdown\n## Output\n" + stamp_block(1) + "\n```"
    text = unstamped().replace("Domain detail.", code)
    assert lint(stamped(text, 1)) == []


@pytest.mark.parametrize(
    ("text", "wording"),
    [
        (make_agent() + stamp_block(1).splitlines()[0] + "\n", "one BEGIN and one END"),
        (unstamped().replace("## Output", "## Results"), "no ## Output heading"),
    ],
)
def test_unstampable_files(text: str, wording: str) -> None:
    with pytest.raises(stamp_sections.StampError, match=wording):
        stamp_sections.stamp(split_lines(text), TEMPLATES[1])


# -- stamp_file(): tier choice and writing ---------------------------------------


@pytest.fixture(name="repo")
def repo_fixture(tmp_path: Path) -> Path:
    """A throwaway repo root holding templates/."""
    (tmp_path / "templates").mkdir()
    for tier in range(1, 6):
        name = f"operating-notes-tier{tier}.md"
        (tmp_path / "templates" / name).write_bytes(
            (ROOT / "templates" / name).read_bytes()
        )
    return tmp_path


def write_agent(repo: Path, category: str, text: str) -> Path:
    """Write text as categories/<category>/sample-agent.md under repo."""
    path = repo / "categories" / category / "sample-agent.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode())
    return path


@pytest.mark.parametrize(
    ("category", "tools", "allow", "tier"),
    [
        ("22-deployment-and-release", "Read, Bash", Allowlist(), 5),
        ("22-deployment-and-release", "Read, Grep", Allowlist(), 1),
        ("08-general-development", "Read, Edit", Allowlist(), 2),
        (
            "08-general-development",
            "Read, Edit",
            Allowlist(tier_overrides={"sample-agent": 5}),
            5,
        ),
    ],
)
def test_stamp_file_chooses_tier(
    repo: Path, category: str, tools: str, allow: Allowlist, tier: int
) -> None:
    path = write_agent(repo, category, unstamped(1, tools=tools))
    message = stamp_sections.stamp_file(path, repo, allow)
    assert message.endswith(f"stamped {path} (tier={tier})")
    assert stamp_block(tier) in path.read_text()


def test_stamp_file_normalises_crlf_and_reports_current(repo: Path) -> None:
    path = write_agent(
        repo, "03-analysis-and-review", make_agent().replace("\n", "\r\n")
    )
    assert "stamped" in stamp_sections.stamp_file(path, repo, Allowlist())
    assert path.read_bytes() == make_agent().encode()
    assert "already current" in stamp_sections.stamp_file(path, repo, Allowlist())


def test_stamp_file_outside_categories(repo: Path) -> None:
    path = repo / "sample-agent.md"
    path.write_text(unstamped())
    with pytest.raises(stamp_sections.StampError, match="categories/NN-"):
        stamp_sections.stamp_file(path, repo, Allowlist())


def test_main_requires_paths(capsys: pytest.CaptureFixture[str]) -> None:
    assert stamp_sections.main([]) == 1
    assert "Usage" in capsys.readouterr().err


def test_main_reports_missing_file(capsys: pytest.CaptureFixture[str]) -> None:
    assert stamp_sections.main(["no/such/file.md"]) == 1
    assert "does not exist" in capsys.readouterr().err
