"""Shared builders for agent-file tests.

make_agent() returns a file that passes every lint rule for its tier; each
test changes one thing and asserts on the rule that fires.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import agent_file
import agent_lint

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = agent_file.load_templates(ROOT / "templates")

# One category per tier, as a path prefix for lint_file().
TIER_DIR = {
    1: "categories/03-analysis-and-review",
    2: "categories/08-general-development",
    3: "categories/14-data-and-database",
    4: "categories/19-infrastructure-as-code",
    5: "categories/22-deployment-and-release",
}

FRONTMATTER = {
    1: {
        "tools": "Read, Grep, Glob",
        "disallowedTools": "Write, Edit, NotebookEdit, Bash",
        "model": "sonnet",
        "color": "green",
    },
    2: {
        "tools": "Read, Write, Edit, Bash, Glob, Grep",
        "model": "sonnet",
        "color": "yellow",
    },
    3: {
        "tools": "Read, Write, Edit, Bash, Glob, Grep",
        "model": "sonnet",
        "color": "orange",
    },
    4: {
        "tools": "Read, Write, Edit, Bash, Glob, Grep",
        "model": "sonnet",
        "color": "red",
        "effort": "high",
        "maxTurns": "40",
    },
    5: {
        "tools": "Read, Write, Edit, Bash, Glob, Grep",
        "model": "sonnet",
        "color": "purple",
        "effort": "high",
        "maxTurns": "25",
    },
}


def stamp_block(tier: int) -> str:
    """The operating-notes block for tier, as in templates/."""
    return "\n".join(TEMPLATES[tier])


def make_agent(
    tier: int = 1,
    name: str = "sample-agent",
    stier: int | None = None,
    **overrides: str | None,
) -> str:
    """A v3 agent file that lints clean for tier.

    overrides replace frontmatter values; None removes a key. stier picks the
    stamped block when it differs from tier.
    """
    stier = stier or tier
    fields: dict[str, str | None] = {
        "name": name,
        "description": '"Reviews sample code for sample defects."',
        **FRONTMATTER[tier],
    }
    fields.update(overrides)
    front = "\n".join(f"{k}: {v}" for k, v in fields.items() if v is not None)
    sections = [
        "You are a sample reviewer.",
        "## Scope\n\nSample scope.",
        "## How you work\n\n1. Read.\n2. Report.\n   Continued.",
        "## Sample domain\n\nDomain detail.",
    ]
    if stier != 1:
        sections.append("## Expert practice\n\nPlan before apply.")
    sections += ["## Output\n\nFindings.", stamp_block(stier)]
    if stier >= 3:
        sections.append("## Rollback\n\n```bash\ngit revert HEAD\n```")
    return f"---\n{front}\n---\n\n" + "\n\n".join(sections) + "\n"


def lint(
    text: str,
    tier: int = 1,
    name: str = "sample-agent",
    allow: agent_file.Allowlist | None = None,
) -> list[agent_lint.Finding]:
    """Lint text as categories/<tier's category>/<name>.md."""
    path = f"{TIER_DIR[tier]}/{name}.md"
    return agent_lint.lint_file(path, text, TEMPLATES, allow or agent_file.Allowlist())


def rules(findings: list[agent_lint.Finding]) -> set[str]:
    """The distinct rules that fired."""
    return {f.rule for f in findings}


def load_compress_descriptions() -> ModuleType:
    """Import scripts/compress-descriptions.py, whose hyphen blocks import."""
    name = "compress_descriptions"
    if name in sys.modules:
        return sys.modules[name]
    path = ROOT / "scripts" / "compress-descriptions.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
