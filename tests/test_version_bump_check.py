"""Behaviour of scripts/version_bump_check.py: which changes need a bump."""

# pylint: disable=missing-function-docstring
# pylint: disable=use-implicit-booleaness-not-comparison

from __future__ import annotations

import json

# Builds throwaway git repos: a fixed argv, never a shell.
import subprocess  # nosec B404
from pathlib import Path

import pytest
import version_bump_check as vbc

CAT = "01-research"
AGENT = f"categories/{CAT}/a-agent.md"
PLUGIN = vbc.PLUGIN_FILE.format(CAT)


def tree(
    version: str = "1.0.0",
    agents: tuple[str, ...] = ("a-agent",),
    market: str = "2.0.0",
    files: dict[str, str] | None = None,
) -> dict[str, str]:
    """A repository tree: one category plugin, the marketplace, and files."""
    plugin = {"version": version, "agents": [f"./{a}.md" for a in agents]}
    return {
        PLUGIN: json.dumps(plugin),
        vbc.MARKETPLACE_FILE: json.dumps({"metadata": {"version": market}}),
        **{f"categories/{CAT}/{name}": text for name, text in (files or {}).items()},
    }


def run_check(
    changed: set[str], base: dict[str, str], head: dict[str, str]
) -> tuple[list[str], list[str]]:
    return vbc.check(changed, base.get, head.get)


# -- Rules ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "parsed"),
    [
        ("1.2.3", (1, 2, 3)),
        ("10.0.0", (10, 0, 0)),
        ("1.2", None),
        ("01.2.3", None),
        ("1.2.3-rc1", None),
        ("", None),
    ],
)
def test_parse_version(text: str, parsed: tuple[int, int, int] | None) -> None:
    assert vbc.parse_version(text) == parsed


@pytest.mark.parametrize(
    ("old", "new", "wording"),
    [
        ("1.0.0", "1.0.1", None),
        ("1.9.0", "1.10.0", None),
        ("1.0.0", "2.0.0", None),
        ("1.0.0", "1.0.0", "must increase"),
        ("1.2.0", "1.1.9", "must increase"),
        ("1.0.0", "v1.0.1", "MAJOR.MINOR.PATCH"),
    ],
)
def test_bump_problem(old: str, new: str, wording: str | None) -> None:
    problem = vbc.bump_problem("x", old, new)
    assert (problem is None) if wording is None else (wording in str(problem))


def test_agent_edit_without_bump_fails() -> None:
    lines, failures = run_check({AGENT}, tree(), tree())
    assert lines == [
        f"{CAT}: agents changed, version 1.0.0 -> 1.0.0",
        "marketplace: metadata.version 2.0.0 -> 2.0.0",
    ]
    assert len(failures) == 2
    assert failures[0] == f"{PLUGIN} version must increase; got 1.0.0 -> 1.0.0"


def test_agent_edit_with_both_bumps_passes() -> None:
    head = tree(version="1.0.1", market="2.0.1")
    assert run_check({AGENT, PLUGIN}, tree(), head)[1] == []


def test_plugin_bump_without_marketplace_bump_fails() -> None:
    _, failures = run_check({AGENT, PLUGIN}, tree(), tree(version="1.1.0"))
    assert failures == [
        f"{vbc.MARKETPLACE_FILE} metadata.version must increase; got 2.0.0 -> 2.0.0"
    ]


def test_readme_only_change_needs_no_bump() -> None:
    readme = f"categories/{CAT}/README.md"
    assert run_check({readme}, tree(), tree()) == ([], [])


def test_unlisted_file_needs_no_bump() -> None:
    # A stray .md not in the agents array isn't shipped; validate-catalog.sh
    # is what fails a file missing from plugin.json.
    stray = f"categories/{CAT}/notes.md"
    assert run_check({stray}, tree(), tree()) == ([], [])


@pytest.mark.parametrize(
    ("base_agents", "head_agents", "changed"),
    [
        (("a-agent",), ("a-agent", "b-agent"), {f"categories/{CAT}/b-agent.md"}),
        (("a-agent", "b-agent"), ("a-agent",), {f"categories/{CAT}/b-agent.md"}),
        (("a-agent",), ("c-agent",), {AGENT, f"categories/{CAT}/c-agent.md"}),
    ],
    ids=["added", "deleted", "renamed"],
)
def test_agent_set_changes_need_a_bump(
    base_agents: tuple[str, ...], head_agents: tuple[str, ...], changed: set[str]
) -> None:
    base, head = tree(agents=base_agents), tree(agents=head_agents)
    lines, failures = run_check(changed | {PLUGIN}, base, head)
    assert lines[0].startswith(f"{CAT}: agents changed")
    assert len(failures) == 2


def test_reordered_agents_array_needs_no_bump() -> None:
    base, head = tree(agents=("a-agent", "b-agent")), tree(
        agents=("b-agent", "a-agent")
    )
    assert run_check({PLUGIN}, base, head) == ([], [])


def test_plugin_metadata_only_change_needs_no_bump() -> None:
    base = tree()
    head = dict(base)
    head[PLUGIN] = json.dumps(
        {"version": "1.0.0", "agents": ["./a-agent.md"], "description": "new"}
    )
    assert run_check({PLUGIN}, base, head) == ([], [])


@pytest.mark.parametrize(
    ("side", "line"), [("base", "category added"), ("head", "category removed")]
)
def test_added_or_removed_category_needs_marketplace_bump(side: str, line: str) -> None:
    base, head = tree(), tree()
    (base if side == "base" else head).pop(PLUGIN)
    lines, failures = run_check({PLUGIN}, base, head)
    assert lines[0] == f"{CAT}: {line}"
    assert failures == [
        f"{vbc.MARKETPLACE_FILE} metadata.version must increase; got 2.0.0 -> 2.0.0"
    ]


def test_categories_touched_ignores_paths_outside_categories() -> None:
    changed = {AGENT, "categories/02-x/README.md", "README.md", "scripts/x.py"}
    assert vbc.categories_touched(changed) == {CAT, "02-x"}


# -- run(): the git layer over a throwaway repo --------------------------------


def git(repo: Path, *args: str) -> str:
    # A fixed argv with no shell; git comes from PATH, as in CI.
    return subprocess.run(  # nosec B603 B607
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def commit(repo: Path, files: dict[str, str]) -> str:
    """Write files into repo, commit everything and return the commit id."""
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "c")
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture(name="repo")
def repo_fixture(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    return tmp_path


def test_run_fails_a_rename_without_bump(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = commit(repo, tree(files={"a-agent.md": "one\n"}))
    git(repo, "mv", AGENT, f"categories/{CAT}/c-agent.md")
    head = commit(repo, {PLUGIN: tree(agents=("c-agent",))[PLUGIN]})
    assert vbc.run(repo, base, head) == 1
    err = capsys.readouterr().err
    assert f"FAIL  {PLUGIN} version must increase" in err
    assert vbc.HINT in err


def test_run_passes_a_bumped_edit(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = commit(repo, tree(files={"a-agent.md": "one\n"}))
    head = commit(
        repo, tree(version="1.0.1", market="2.1.0", files={"a-agent.md": "two\n"})
    )
    assert vbc.run(repo, base, head) == 0
    assert "version 1.0.0 -> 1.0.1" in capsys.readouterr().out


def test_run_without_agent_changes(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = commit(repo, tree(files={"a-agent.md": "one\n", "README.md": "r\n"}))
    head = commit(repo, {f"categories/{CAT}/README.md": "r2\n", "README.md": "x\n"})
    assert vbc.run(repo, base, head) == 0
    assert "no version bump needed" in capsys.readouterr().out


def test_run_rejects_a_missing_revision(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    head = commit(repo, tree())
    assert vbc.run(repo, "f" * 40, head) == 1
    assert "is not a commit in this checkout" in capsys.readouterr().err


def test_run_skips_the_all_zero_base(capsys: pytest.CaptureFixture[str]) -> None:
    assert vbc.run(Path(), vbc.NO_COMMIT, "HEAD") == 0
    assert "nothing to check" in capsys.readouterr().out
