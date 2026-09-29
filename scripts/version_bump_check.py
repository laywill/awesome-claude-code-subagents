#!/usr/bin/env python3
"""Fail when a category's agents change without a version bump (#382).

Called from .github/workflows/validate.yml with two git revisions:

    python3 scripts/version_bump_check.py <base> [<head>]

On a pull request, base is the PR's base commit and head is the merge commit
GitHub checks out, so the diff is exactly what merging would change. On a push
to main, base is the previous tip, so a merge that slipped past the PR check
still turns main red.

Each category's plugin.json pins "version", and Claude Code keeps an installed
plugin on its cached copy until that string changes. A change to what a
category ships, merged without a bump, therefore never reaches existing
installs: a shadow release. A category's change is release-relevant when an
agent file listed in its plugin.json "agents" array, on either side, is added,
edited, deleted or renamed, when that array changes, or when the category
itself is added or removed. README files are not shipped and don't count.

For each release-relevant category, plugin.json "version" must be strictly
greater on head than on base, as MAJOR.MINOR.PATCH. If any category is
release-relevant, .claude-plugin/marketplace.json "metadata.version" must be
strictly greater too. Only that the version went up is checked; whether the
change is major, minor or patch is for review. The marketplace entry's own
"version" must equal plugin.json's, which `claude plugin validate --strict`
already enforces.

Standard library only: CI runs it with the runner's system Python.
"""

from __future__ import annotations

import argparse
import json
import re

# Runs git with a fixed argv, never a shell.
import subprocess  # nosec B404
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

MARKETPLACE_FILE = ".claude-plugin/marketplace.json"
PLUGIN_FILE = "categories/{}/.claude-plugin/plugin.json"
CATEGORY_RE = re.compile(r"categories/([^/]+)/")
VERSION_RE = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
NO_COMMIT = "0" * 40
HINT = (
    "Bump the category's plugin.json version, set its entry in "
    f"{MARKETPLACE_FILE} to match, and bump that file's metadata.version."
)

# The text of a repository path at one revision, or None where it doesn't exist.
Reader = Callable[[str], str | None]


@dataclass(frozen=True)
class Plugin:
    """What a category's plugin.json says at one revision."""

    version: str
    agents: frozenset[str]


@dataclass(frozen=True)
class Outcome:
    """One release-relevant category: a line for the report, and any failure."""

    line: str
    failure: str | None = None


# -- Reading manifests ---------------------------------------------------------


def load_plugin(read: Reader, category: str) -> Plugin | None:
    """A category's plugin.json, with agent paths made repository-relative."""
    text = read(PLUGIN_FILE.format(category))
    if text is None:
        return None
    data = json.loads(text)
    agents = frozenset(
        f"categories/{category}/{str(agent).removeprefix('./')}"
        for agent in data.get("agents", [])
    )
    return Plugin(str(data.get("version", "")), agents)


def marketplace_version(read: Reader) -> str:
    """The marketplace's metadata.version, or "" where there is none."""
    text = read(MARKETPLACE_FILE)
    if text is None:
        return ""
    return str(json.loads(text).get("metadata", {}).get("version", ""))


# -- Rules ---------------------------------------------------------------------


def parse_version(text: str) -> tuple[int, int, int] | None:
    """MAJOR.MINOR.PATCH as integers, or None for any other form."""
    match = VERSION_RE.fullmatch(text)
    if not match:
        return None
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


def bump_problem(what: str, old: str, new: str) -> str | None:
    """Why new is not a valid bump of old, or None when it is."""
    old_v, new_v = parse_version(old), parse_version(new)
    if old_v is None or new_v is None:
        return f"{what} must be MAJOR.MINOR.PATCH on both sides; got {old!r} -> {new!r}"
    if new_v <= old_v:
        return f"{what} must increase; got {old} -> {new}"
    return None


def categories_touched(changed: Iterable[str]) -> set[str]:
    """The category directories that the changed paths fall under."""
    return {m.group(1) for path in changed if (m := CATEGORY_RE.match(path))}


def release_relevant(
    changed: set[str], base: Plugin | None, head: Plugin | None
) -> bool:
    """Whether a category's change alters what its plugin ships."""
    if base is None or head is None:
        return (base is None) != (head is None)
    return base.agents != head.agents or bool(changed & (base.agents | head.agents))


def check_category(
    category: str, changed: set[str], read_base: Reader, read_head: Reader
) -> Outcome | None:
    """The outcome for one touched category, or None if it ships nothing new."""
    base, head = load_plugin(read_base, category), load_plugin(read_head, category)
    if not release_relevant(changed, base, head):
        return None
    if base is None:
        return Outcome(f"{category}: category added")
    if head is None:
        return Outcome(f"{category}: category removed")
    what = f"{PLUGIN_FILE.format(category)} version"
    return Outcome(
        f"{category}: agents changed, version {base.version} -> {head.version}",
        bump_problem(what, base.version, head.version),
    )


def check(
    changed: set[str], read_base: Reader, read_head: Reader
) -> tuple[list[str], list[str]]:
    """Report lines and failures for the change from base to head."""
    outcomes = [
        outcome
        for category in sorted(categories_touched(changed))
        if (outcome := check_category(category, changed, read_base, read_head))
    ]
    if not outcomes:
        return [], []
    old, new = marketplace_version(read_base), marketplace_version(read_head)
    outcomes.append(
        Outcome(
            f"marketplace: metadata.version {old or '(none)'} -> {new or '(none)'}",
            bump_problem(f"{MARKETPLACE_FILE} metadata.version", old, new),
        )
    )
    return [o.line for o in outcomes], [o.failure for o in outcomes if o.failure]


# -- Git -----------------------------------------------------------------------


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git in repo and capture its output."""
    # A fixed argv with no shell; git comes from PATH, as in CI.
    return subprocess.run(  # nosec B603 B607
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def reader(repo: Path, rev: str) -> Reader:
    """A Reader for the tree at rev."""

    def read(path: str) -> str | None:
        shown = git(repo, "show", f"{rev}:{path}")
        return shown.stdout if shown.returncode == 0 else None

    return read


def changed_paths(repo: Path, base: str, head: str) -> set[str]:
    """Paths under categories/ that differ; a rename lists both of its sides."""
    diff = git(repo, "diff", "--name-only", "--no-renames", "-z", base, head)
    if diff.returncode != 0:
        raise RuntimeError(diff.stderr.strip())
    return {path for path in diff.stdout.split("\0") if path.startswith("categories/")}


def run(repo: Path, base: str, head: str) -> int:
    """Check base..head in repo, print the result and return the exit code."""
    if base == NO_COMMIT:
        print("No previous commit to compare against; nothing to check.")
        return 0
    for rev in (base, head):
        if git(
            repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"
        ).returncode:
            print(f"FAIL  {rev} is not a commit in this checkout", file=sys.stderr)
            return 1
    lines, failures = check(
        changed_paths(repo, base, head), reader(repo, base), reader(repo, head)
    )
    if not lines:
        print("No release-relevant agent changes; no version bump needed.")
        return 0
    # Flushed so the report precedes the failures when both streams share a log.
    print("\n".join(lines), flush=True)
    if failures:
        print(file=sys.stderr)
        for failure in failures:
            print(f"FAIL  {failure}", file=sys.stderr)
        print(f"\n{HINT}", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse the arguments and run the check from the current directory."""
    parser = argparse.ArgumentParser(
        description="Fail when a category's agents change without a version bump."
    )
    parser.add_argument("base", help="the revision before the change")
    parser.add_argument("head", nargs="?", default="HEAD", help="default: HEAD")
    args = parser.parse_args(argv)
    return run(Path.cwd(), args.base, args.head)


if __name__ == "__main__":
    sys.exit(main())
