"""Frontmatter rules for scripts/agent_lint.py: keys, values and tier rules.

Every check reports through an Emit callback, so this module knows nothing of
findings or files. Overrides in scripts/lint-allowlist.txt never change the
tier these rules use; they read the category tier.
"""

from __future__ import annotations

import re

from agent_file import Allowlist, Frontmatter
from lint_model import Emit, Severity

C = Severity.RATCHETED

ALLOWED_KEYS = {
    "name",
    "description",
    "tools",
    "model",
    "color",
    "disallowedTools",
    "effort",
    "maxTurns",
}
FORBIDDEN_KEYS = {"permissionMode", "hooks", "mcpServers", "initialPrompt"}
NOT_USED_KEYS = {
    "isolation",
    "memory",
    "skills",
    "background",
    "omitClaudeMd",
    "experimental",
}
REAL_TOOLS = {
    "Agent",
    "AskUserQuestion",
    "Bash",
    "Edit",
    "ExitPlanMode",
    "Glob",
    "Grep",
    "LSP",
    "NotebookEdit",
    "PowerShell",
    "Read",
    "Skill",
    "Task",
    "TodoWrite",
    "WebFetch",
    "WebSearch",
    "Write",
}
MODELS = ("haiku", "sonnet", "opus")
TIER_COLOR = {1: "green", 2: "yellow", 3: "orange", 4: "red", 5: "purple"}
TIER_MAX_TURNS = {4: "40", 5: "25"}
NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
ALLOWLIST_NOTE = "scripts/lint-allowlist.txt"


def check_frontmatter(fm: Frontmatter, tier: int, allow: Allowlist, emit: Emit) -> None:
    """Keys, values and per-tier rules for one file in a category of tier."""
    check_keys(fm, emit)
    name, model = fm.get("name"), fm.get("model")
    if not NAME_RE.fullmatch(name):
        emit(C, "name-format", f"name '{name}' is not kebab-case")
    check_description(fm, emit)
    if model not in MODELS:
        emit(C, "model-value", f"model '{model}' is not haiku, sonnet or opus")

    tools = fm.tool_set("tools")
    disallowed = fm.tool_set("disallowedTools")
    check_tools(tools, disallowed, emit)

    color = fm.get("color")
    if color != TIER_COLOR[tier]:
        emit(
            C,
            "color-tier",
            f"color is '{color or '<absent>'}', tier {tier} requires "
            f"'{TIER_COLOR[tier]}'",
        )
    if tier == 1:
        check_tier1_bash(allow.allows(name, "tier1-bash"), tools, disallowed, emit)
    sonnet_exempt = allow.allows(name, "sonnet-instead-of-opus")
    check_effort(model, fm.get("effort"), tier, sonnet_exempt, emit)
    check_max_turns(fm.get("maxTurns"), tier, emit)


def check_keys(fm: Frontmatter, emit: Emit) -> None:
    """Only the keys the catalog uses; misspellings are silently ignored."""
    for key in fm.keys:
        if key in ALLOWED_KEYS:
            continue
        if key in FORBIDDEN_KEYS:
            msg = f"'{key}' is forbidden: plugin agents ignore it"
        elif key in NOT_USED_KEYS:
            msg = f"'{key}' is a Claude Code field this catalog doesn't use"
        else:
            msg = (
                f"'{key}' is not a recognised key "
                "(Claude Code silently ignores misspellings)"
            )
        emit(C, "frontmatter-key", msg)


def check_description(fm: Frontmatter, emit: Emit) -> None:
    """One line, no examples, at most 250 characters."""
    desc = fm.get("description")
    if len(desc) > 250:
        emit(
            C,
            "description-length",
            f"description is {len(desc)} characters, over the 250 limit",
        )
    if "<example" in desc:
        emit(C, "description-format", "description holds an <example> block")
    # A block scalar (| or >) reads back as its indicator; an escaped \n is a
    # second line in disguise.
    block_scalar = re.fullmatch(r"[|>][-+]?", desc)
    if fm.description_multiline or block_scalar or "\\n" in desc:
        emit(C, "description-format", "description spans more than one line")


def check_tools(tools: list[str], disallowed: list[str], emit: Emit) -> None:
    """Real tool names, and none in both lists."""
    check_tool_names("tools", tools, emit)
    check_tool_names("disallowedTools", disallowed, emit)
    for tool in disallowed:
        if tool in tools:
            emit(C, "tools-overlap", f"'{tool}' is in both tools and disallowedTools")


def check_tool_names(key: str, tools: list[str], emit: Emit) -> None:
    """Every entry is a plain, real tool name."""
    for tool in tools:
        if "(" in tool or tool.startswith("mcp__"):
            emit(C, "tools-format", f"{key} holds a specifier or MCP pattern: {tool}")
        elif tool not in REAL_TOOLS:
            emit(C, "tools-format", f"{key} holds an unrecognised tool name: {tool}")


def check_tier1_bash(
    exempt: bool, tools: list[str], disallowed: list[str], emit: Emit
) -> None:
    """Tier 1 disallows Bash unless the allowlist says the role needs it."""
    if "Bash" in tools and not exempt:
        emit(
            C,
            "tier1-bash",
            f"tier 1 tools hold Bash with no tier1-bash entry in {ALLOWLIST_NOTE}",
        )
    elif "Bash" not in tools and "Bash" not in disallowed:
        emit(C, "tier1-bash", "tier 1 disallowedTools must list Bash")


def check_effort(
    model: str, effort: str, tier: int, sonnet_exempt: bool, emit: Emit
) -> None:
    """effort: high on Tier 4-5 sonnet, or an allowlisted Tier 1-3 sonnet."""
    if effort and effort != "high":
        emit(
            C,
            "effort",
            f"effort '{effort}' is not allowed; the only allowed value is high",
        )
    if effort and model in ("haiku", "opus"):
        emit(C, "effort", f"effort must be absent on {model}")
    if model == "sonnet":
        check_sonnet_effort(effort, tier, sonnet_exempt, emit)


def check_sonnet_effort(
    effort: str, tier: int, sonnet_exempt: bool, emit: Emit
) -> None:
    """Required on Tier 4-5; on Tier 1-3 only with an allowlist entry."""
    if tier >= 4 and effort != "high":
        emit(C, "effort", f"tier {tier} sonnet agents require effort: high")
    if tier <= 3 and effort and not sonnet_exempt:
        emit(
            C,
            "effort",
            f"tier {tier} sets effort without a sonnet-instead-of-opus entry in "
            f"{ALLOWLIST_NOTE}",
        )


def check_max_turns(max_turns: str, tier: int, emit: Emit) -> None:
    """40 on Tier 4, 25 on Tier 5, absent below."""
    if max_turns and not re.fullmatch(r"[1-9][0-9]*", max_turns):
        emit(C, "maxturns", f"maxTurns '{max_turns}' is not a positive integer")
    if tier <= 3 and max_turns:
        emit(C, "maxturns", f"tier {tier} must not set maxTurns")
    if tier in TIER_MAX_TURNS and max_turns != TIER_MAX_TURNS[tier]:
        emit(
            C,
            "maxturns",
            f"tier {tier} requires maxTurns: {TIER_MAX_TURNS[tier]}, got '{max_turns}'",
        )
