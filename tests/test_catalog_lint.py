"""Behaviour of scripts/catalog_lint.py: the ratchet, allowlist and templates."""

# pytest isn't installed where MegaLinter runs pylint; the pytest job fails
# on an import that is really missing.
# pylint: disable=import-error,missing-function-docstring
# pylint: disable=use-implicit-booleaness-not-comparison

from __future__ import annotations

from pathlib import Path

import agent_file
import catalog_lint
import pytest
from agent_lint import Finding
from builders import ROOT, TEMPLATES, TIER_DIR, make_agent


def test_parse_enforced() -> None:
    text = "# comment\n\n03-analysis-and-review\n  14-data-and-database  # note\r\n"
    assert catalog_lint.parse_enforced(text) == [
        "03-analysis-and-review",
        "14-data-and-database",
    ]


@pytest.mark.parametrize(
    ("line", "wording"),
    [
        ("a-agent: tier=5", "is not '<agent-name>: <rule> # <reason>'"),
        ("a-agent: tier=5 #   ", "has no reason"),
        ("nobody: tier=5 # why", "not an agent"),
        ("a-agent: tier=7 # why", "unknown rule"),
        ("a-agent: tier1-bash # why", "applies only to Tier 1"),
        ("b-agent: sonnet-instead-of-opus # why", "applies only to Tier 1-3"),
    ],
)
def test_check_allowlist(line: str, wording: str) -> None:
    failures = catalog_lint.check_allowlist(line + "\n", {"a-agent": 2, "b-agent": 4})
    assert len(failures) == 1 and wording in failures[0], failures


def test_check_allowlist_accepts_valid_and_rejects_repeats() -> None:
    tiers = {"a-agent": 1, "b-agent": 3}
    text = "a-agent: tier1-bash # why\nb-agent: sonnet-instead-of-opus # why\n"
    assert catalog_lint.check_allowlist(text, tiers) == []
    failures = catalog_lint.check_allowlist(
        text + "a-agent: tier1-bash # again\n", tiers
    )
    assert failures == [f"{agent_file.ALLOWLIST_FILE}:3 repeats a-agent: tier1-bash"]


def test_templates_match_guidelines_section_7() -> None:
    guidelines = agent_file.read_text(ROOT / catalog_lint.GUIDELINES_FILE)
    assert catalog_lint.check_templates(guidelines, TEMPLATES) == []


def test_check_templates_reports_drift_and_missing() -> None:
    guide = (
        "## 7. Notes\n\n```markdown\none\n```\n\n## 8. Next\n\n```markdown\nx\n```\n"
    )
    failures = catalog_lint.check_templates(guide, {1: ["one"], 2: ["two"]})
    assert failures[0].endswith(
        "differs from the tier 2 block in AGENT_SECURITY_GUIDELINES.md §7"
    )
    assert failures[1:] == [
        f"templates/operating-notes-tier{t}.md does not exist" for t in (3, 4, 5)
    ]


def test_ratchet() -> None:
    def finding(cls: str, category: str) -> Finding:
        return Finding(cls, "r", f"categories/{category}/x.md", "m")

    findings = [
        finding("C", "03-enforced"),
        finding("C", "04-other"),
        finding("F", "04-other"),
        finding("W", "03-enforced"),
    ]
    failures, warnings = catalog_lint.ratchet(findings, {"03-enforced"})
    assert failures == [findings[0], findings[2]]
    assert warnings == [findings[1], findings[3]]


# -- run(): the whole pipeline over a throwaway repo ---------------------------


@pytest.fixture(name="repo")
def repo_fixture(tmp_path: Path) -> Path:
    """A minimal repo: templates, guidelines, ratchet files, one clean agent."""
    for rel in ["templates", "scripts"]:
        (tmp_path / rel).mkdir()
    for tier in range(1, 6):
        name = f"templates/operating-notes-tier{tier}.md"
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    guidelines = catalog_lint.GUIDELINES_FILE
    (tmp_path / guidelines).write_bytes((ROOT / guidelines).read_bytes())
    (tmp_path / catalog_lint.ENFORCED_FILE).write_text("# none yet\n")
    (tmp_path / agent_file.ALLOWLIST_FILE).write_text("# none yet\n")
    add_agent(tmp_path, "clean-agent", make_agent(name="clean-agent"))
    return tmp_path


def add_agent(repo: Path, name: str, text: str) -> None:
    """Write a tier 1 agent file into repo."""
    path = repo / TIER_DIR[1] / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_run_clean_repo(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert catalog_lint.run(repo, verbose=False, detail=set()) == 0
    assert "warning" not in capsys.readouterr().out


def test_run_warns_outside_enforced_category(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    add_agent(repo, "bad-agent", make_agent(name="bad-agent", color="blue"))
    assert catalog_lint.run(repo, verbose=True, detail=set()) == 0
    out = capsys.readouterr().out
    assert "WARN  categories/03-analysis-and-review/bad-agent.md: [color-tier]" in out
    assert "1 warning(s), not enforced" in out


def test_run_fails_inside_enforced_category(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    add_agent(repo, "bad-agent", make_agent(name="bad-agent", color="blue"))
    (repo / catalog_lint.ENFORCED_FILE).write_text("03-analysis-and-review\n")
    assert catalog_lint.run(repo, verbose=False, detail=set()) == 1
    assert "[color-tier]" in capsys.readouterr().err


def test_run_fails_on_missing_ratchet_files(repo: Path) -> None:
    (repo / catalog_lint.ENFORCED_FILE).unlink()
    (repo / agent_file.ALLOWLIST_FILE).unlink()
    assert catalog_lint.run(repo, verbose=False, detail=set()) == 2


def test_run_fails_on_unknown_enforced_category(repo: Path) -> None:
    (repo / catalog_lint.ENFORCED_FILE).write_text("99-nothing\n")
    assert catalog_lint.run(repo, verbose=False, detail=set()) == 1


def test_run_fails_on_template_drift(repo: Path) -> None:
    (repo / "templates/operating-notes-tier3.md").write_text("changed\n")
    assert catalog_lint.run(repo, verbose=False, detail=set()) == 1
