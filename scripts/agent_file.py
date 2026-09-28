"""Reading agent definition files: the primitives under scripts/lint_model.py.

Line endings, frontmatter, fence syntax, a file's tier and its stamp tier,
the allowlist and the templates. scripts/lint_model.py builds its parsed
model from these, and the lint, the catalog run and the stamper all read
through one or the other, so they can't disagree. The module name uses
underscores, unlike the hyphenated shell scripts beside it, so that it can be
imported.

Standard library only: CI runs it with the runner's system Python.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_FILE = "scripts/lint-allowlist.txt"
TEMPLATE_DIR = "templates"

BEGIN_MARK = "<!-- BEGIN GENERATED: operating-notes tier="
END_MARK = "<!-- END GENERATED: operating-notes -->"

WRITE_CAPABLE_TOOLS = {"Bash", "Write", "Edit", "NotebookEdit"}

KEY_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*:")
COMMENT_OR_BLANK_RE = re.compile(r"[ \t]*(#|$)")
BLANK_RE = re.compile(r"[ \t]*$")
TIER_OVERRIDE_RE = re.compile(r"tier=([1-5])")


def split_lines(text: str) -> list[str]:
    """Split on LF only, dropping one trailing CR per line.

    A lone CR is not a line break: that is how git and editorconfig-checker
    see such a file, so the lint must too.
    """
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [line.removesuffix("\r") for line in lines]


def read_text(path: Path) -> str:
    """Read a file as UTF-8 without failing on stray bytes."""
    return path.read_bytes().decode("utf-8", "surrogateescape")


def category_tier(path: str) -> int | None:
    """The risk tier of an agent file, from its category directory number."""
    match = re.search(r"(?:^|/)categories/([0-9]{2})-[^/]*/[^/]*$", path)
    if not match:
        return None
    num = int(match.group(1))
    for tier, upper in ((1, 6), (2, 13), (3, 17), (4, 21), (5, 24)):
        if 1 <= num <= upper:
            return tier
    return None


def fence_open(stripped: str) -> tuple[str, int] | None:
    """(fence char, length) when a leading-whitespace-stripped line opens one."""
    char = stripped[:1]
    if char not in ("`", "~"):
        return None
    length = len(stripped) - len(stripped.lstrip(char))
    return (char, length) if length >= 3 else None


def closes_fence(stripped: str, char: str, length: int) -> bool:
    """Whether a stripped line closes the fence opened with char * length."""
    count = len(stripped) - len(stripped.lstrip(char))
    return count >= length and stripped[count:].strip(" \t") == ""


@dataclass
class Frontmatter:
    """The frontmatter block of one agent file."""

    values: dict[str, str] = field(default_factory=dict)
    keys: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    description_multiline: bool = False
    closed: bool = False
    body_start: int = 0  # index into the file's lines of the first body line

    def get(self, key: str) -> str:
        """The value for key, or "" when absent."""
        return self.values.get(key, "")

    def add(self, line: str) -> str:
        """Record a "key: value" line, unquoting the value; return the key."""
        key, _, value = line.partition(":")
        value = value.strip(" \t")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key in self.values:
            self.duplicates.append(key)
        self.values[key] = value
        self.keys.append(key)
        return key

    def tool_set(self, key: str) -> list[str]:
        """The comma-separated entries of tools or disallowedTools."""
        return [t.strip(" \t") for t in self.get(key).split(",") if t.strip(" \t")]


def parse_frontmatter(lines: list[str]) -> Frontmatter | None:
    """Parse the leading --- block; None when the file doesn't open with one."""
    if not lines or lines[0] != "---":
        return None
    fm = Frontmatter()
    last_key = ""
    for i, line in enumerate(lines[1:], start=1):
        if line == "---":
            fm.closed = True
            fm.body_start = i + 1
            return fm
        if KEY_RE.match(line):
            last_key = fm.add(line)
        elif not COMMENT_OR_BLANK_RE.match(line) and last_key == "description":
            fm.description_multiline = True
    fm.body_start = len(lines)
    return fm


@dataclass
class Allowlist:
    """scripts/lint-allowlist.txt, as the lint and the stamper read it."""

    tier_overrides: dict[str, int] = field(default_factory=dict)
    exemptions: set[tuple[str, str]] = field(default_factory=set)

    @classmethod
    def parse(cls, text: str) -> Allowlist:
        """Read entries leniently; catalog_lint.check_allowlist() reports bad lines."""
        allow = cls()
        for line in split_lines(text):
            line = line.split("#", 1)[0]
            name, sep, rule = line.partition(":")
            if not sep:
                continue
            name, rule = name.strip(), rule.strip()
            override = TIER_OVERRIDE_RE.fullmatch(rule)
            if override:
                allow.tier_overrides[name] = int(override.group(1))
            elif name:
                allow.exemptions.add((name, rule))
        return allow

    def allows(self, name: str, rule: str) -> bool:
        """Whether name has a reviewed exemption from rule."""
        return (name, rule) in self.exemptions


def stamp_tier(name: str, tools: list[str], tier: int, allow: Allowlist) -> int:
    """The operating-notes tier for a file, per CLAUDE.md "Stamp tier".

    An allowlist override wins; otherwise a file whose tools can't change
    anything takes the Tier 1 notes; otherwise the category tier.
    """
    if name in allow.tier_overrides:
        return allow.tier_overrides[name]
    if WRITE_CAPABLE_TOOLS.intersection(tools):
        return tier
    return 1


def load_templates(template_dir: Path) -> dict[int, list[str]]:
    """The operating-notes template lines for each tier that has one."""
    templates = {}
    for tier in range(1, 6):
        path = template_dir / f"operating-notes-tier{tier}.md"
        if path.is_file():
            templates[tier] = split_lines(read_text(path))
    return templates
