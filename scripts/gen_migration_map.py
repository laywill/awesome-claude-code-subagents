#!/usr/bin/env python3
"""Generate the agent and plugin migration map between two git refs.

Reads everything from git objects (`git ls-tree`, `git show`), so no checkout
is needed and the working tree is never touched. Standard library only.

    python planning/v3/gen_migration_map.py v2.2.0 origin/release/v3.0.0 \
        --overlay planning/v3/migration-overlay.json \
        --out planning/v3/migration-v2.2.0-to-train.json

Fates computed from the two trees alone:
    unchanged  same name, same category directory
    moved      same name, other category directory
    removed    name absent at the new ref
    added      name absent at the old ref

The overlay (hand-reviewed, keyed by old agent name) refines `removed` into
`renamed`, `merged` or `deleted`, with `to`, `pr` and `note`, plus an optional
`also` list for an agent whose scope was split across more than one successor
(`to` is the primary one; tools and model are compared against it). An overlay entry
only applies to an agent the trees say is removed; entries that no longer
apply, and removed agents with no entry, are reported so the overlay can be
kept honest after a regroup.

`--category <dir>` restricts both sides to one category directory (used to
diff an uplift branch against the train for its own category only).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

AGENT_RE = re.compile(r"^categories/([^/]+)/([^/]+)\.md$")
PLUGIN_RE = re.compile(r"^categories/([^/]+)/\.claude-plugin/plugin\.json$")
FRONTMATTER_KEYS = ("tools", "model", "disallowedTools")
OVERLAY_FATES = {"renamed", "merged", "deleted"}


def git(*args: str) -> str:
    """Run git and return stdout as text."""
    done = subprocess.run(
        ["git", *args], check=True, capture_output=True, encoding="utf-8"
    )
    return done.stdout


def frontmatter(text: str) -> dict[str, str]:
    """Return the top-level scalar keys of a file's YAML frontmatter."""
    lines = text.replace("\r", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip("\"'")
    return fields


def tool_set(value: str | None) -> list[str]:
    """Split a `tools` value into a sorted list of tool names."""
    if not value:
        return []
    return sorted({t.strip() for t in value.strip("[]").split(",") if t.strip()})


def snapshot(ref: str, category: str | None) -> dict[str, Any]:
    """Read every agent and plugin manifest at `ref`."""
    paths = git("ls-tree", "-r", "--name-only", ref, "--", "categories/").splitlines()
    plugins: dict[str, dict[str, Any]] = {}
    for path in paths:
        match = PLUGIN_RE.match(path)
        if match and category in (None, match.group(1)):
            manifest = json.loads(git("show", f"{ref}:{path}"))
            plugins[match.group(1)] = {
                "dir": match.group(1),
                "name": manifest.get("name"),
                "version": manifest.get("version"),
                "agent_count": len(manifest.get("agents", [])),
            }
    agents: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for path in paths:
        match = AGENT_RE.match(path)
        if not match or match.group(2) == "README":
            continue
        cat, name = match.groups()
        if category not in (None, cat):
            continue
        if name in agents:
            duplicates.append(name)
        fields = frontmatter(git("show", f"{ref}:{path}"))
        agents[name] = {
            "category": cat,
            "plugin": plugins.get(cat, {}).get("name"),
            "tools": tool_set(fields.get("tools")),
            "tools_declared": "tools" in fields,
            "disallowedTools": tool_set(fields.get("disallowedTools")),
            "model": fields.get("model"),
        }
    marketplace = json.loads(git("show", f"{ref}:.claude-plugin/marketplace.json"))
    return {
        "agents": agents,
        "plugins": plugins,
        "duplicates": duplicates,
        "marketplace": {
            "version": marketplace.get("metadata", {}).get("version"),
            "has_renames_key": "renames" in marketplace
            or "renames" in marketplace.get("metadata", {}),
            "plugin_names": sorted(p.get("name") for p in marketplace.get("plugins", [])),
        },
    }


def tools_direction(old: list[str], new: list[str]) -> str:
    """Classify a change of `tools` between two versions of an agent."""
    a, b = set(old), set(new)
    if a == b:
        return "same"
    if a < b:
        return "widened"
    if b < a:
        return "narrowed"
    return "changed"


def side(prefix: str, info: dict[str, Any] | None) -> dict[str, Any]:
    """Flatten one side of an agent row."""
    keys = ("category", "plugin", "tools", "disallowedTools", "model")
    return {f"{prefix}_{k}": (info[k] if info else None) for k in keys}


def agent_rows(
    old: dict[str, Any], new: dict[str, Any], overlay: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    """Build one row per agent name seen at either ref, overlay applied."""
    rows: list[dict[str, Any]] = []
    succeeded_by: dict[str, list[str]] = {}
    problems: dict[str, list[str]] = {
        "removed_without_overlay": [],
        "overlay_not_applicable": [],
        "overlay_target_missing": [],
        "overlay_bad_fate": [],
    }
    for name in sorted(set(old) | set(new)):
        o, n = old.get(name), new.get(name)
        if o and n:
            fate = "unchanged" if o["category"] == n["category"] else "moved"
        else:
            fate = "removed" if o else "added"
        row: dict[str, Any] = {"name": name, "fate": fate, "tree_fate": fate}
        row.update(side("old", o))
        row.update(side("new", n))
        row.update({"to": None, "also": [], "pr": None, "note": None})
        if fate == "removed":
            entry = overlay.get(name)
            if entry is None:
                problems["removed_without_overlay"].append(name)
            elif entry.get("fate") not in OVERLAY_FATES:
                problems["overlay_bad_fate"].append(name)
            else:
                row.update({k: entry.get(k) for k in ("fate", "to", "pr", "note")})
                row["also"] = list(entry.get("also", []))
                for target in [entry.get("to"), *row["also"]]:
                    if not target:
                        continue
                    succeeded_by.setdefault(target, []).append(name)
                    if target not in new:
                        problems["overlay_target_missing"].append(f"{name} -> {target}")
        elif name in overlay and not name.startswith("_"):
            problems["overlay_not_applicable"].append(name)
        rows.append(row)
    for row in rows:
        row["from"] = sorted(succeeded_by.get(row["name"], []))
        compare_to = new.get(row["to"]) if row["to"] else new.get(row["name"])
        if row["old_tools"] is not None and compare_to:
            row["tools_change"] = tools_direction(row["old_tools"], compare_to["tools"])
            row["model_change"] = row["old_model"] != compare_to["model"]
            if row["to"]:
                row.update(side("new", compare_to))
        else:
            row["tools_change"] = None
            row["model_change"] = None
    return rows, problems


def plugin_rows(old: dict[str, Any], new: dict[str, Any]) -> list[dict[str, Any]]:
    """Pair plugins by directory, then by name where a directory vanished."""
    rows = []
    new_by_name = {p["name"]: p for p in new.values()}
    claimed: set[str] = set()
    for cat in sorted(old):
        o = old[cat]
        n = new.get(cat) or new_by_name.get(o["name"])
        if n:
            claimed.add(n["dir"])
        changes = []
        if not n:
            changes.append("removed")
        else:
            changes += [k for k in ("dir", "name", "version") if o[k] != n[k]]
        rows.append({
            "old_dir": cat, "old_name": o["name"], "old_version": o["version"],
            "old_agent_count": o["agent_count"],
            "new_dir": n["dir"] if n else None, "new_name": n["name"] if n else None,
            "new_version": n["version"] if n else None,
            "new_agent_count": n["agent_count"] if n else None,
            "changed": changes,
        })
    for cat in sorted(set(new) - claimed):
        n = new[cat]
        rows.append({
            "old_dir": None, "old_name": None, "old_version": None,
            "old_agent_count": None, "new_dir": cat, "new_name": n["name"],
            "new_version": n["version"], "new_agent_count": n["agent_count"],
            "changed": ["added"],
        })
    return rows


def count(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    """Tally rows by the value of `key`, skipping None."""
    out: dict[str, int] = {}
    for row in rows:
        if row[key] is not None:
            out[str(row[key])] = out.get(str(row[key]), 0) + 1
    return dict(sorted(out.items()))


def print_summary(doc: dict[str, Any]) -> None:
    """Print the compact, human-readable summary."""
    s = doc["summary"]
    print(f"{doc['old_ref']} -> {doc['new_ref']}"
          + (f"  [category {doc['category']}]" if doc["category"] else ""))
    print(f"agents: {s['agents_old']} old, {s['agents_new']} new")
    print(f"fates (tree only): {s['tree_fates']}")
    print(f"fates (with overlay): {s['fates']}")
    for row in doc["agents"]:
        if row["fate"] == "unchanged":
            continue
        arrow = row["to"] or (row["name"] if row["fate"] in ("moved", "added") else "-")
        arrow += "".join(f" (+{a})" for a in row["also"])
        src = "-" if row["fate"] == "added" else row["name"]
        extra = f"  from={','.join(row['from'])}" if row["from"] else ""
        cats = f"{row['old_category'] or '-'} -> {row['new_category'] or '-'}"
        print(f"  {row['fate']:9} {src} -> {arrow}  PR={row['pr'] or '-'}  [{cats}]{extra}")
    print(f"tools (agents with a successor): {s['tools_change']}")
    for kind in ("narrowed", "changed", "widened"):
        for row in doc["agents"]:
            if row["tools_change"] == kind:
                lost = sorted(set(row["old_tools"]) - set(row["new_tools"]))
                gained = sorted(set(row["new_tools"]) - set(row["old_tools"]))
                target = f" (as {row['to']})" if row["to"] else ""
                print(f"  {kind:8} {row['name']}{target}: -{lost} +{gained}")
    print(f"model changed: {s['model_changed']}")
    for row in doc["agents"]:
        if row["model_change"]:
            print(f"  {row['name']}: {row['old_model']} -> {row['new_model']}")
    changed = [p for p in doc["plugins"] if p["changed"]]
    print(f"plugins: {s['plugins_old']} old, {s['plugins_new']} new; "
          f"dir changed {s['plugin_dir_changed']}, name changed {s['plugin_name_changed']}, "
          f"version changed {s['plugin_version_changed']}, "
          f"added {s['plugins_added']}, removed {s['plugins_removed']}")
    for p in changed:
        print(f"  {p['old_dir']} {p['old_name']} {p['old_version']} -> "
              f"{p['new_dir']} {p['new_name']} {p['new_version']}  {p['changed']}")
    print(f"marketplace: {doc['marketplace']}")
    for key, names in doc["overlay_problems"].items():
        if names:
            print(f"OVERLAY {key}: {names}")


def main() -> int:
    """Parse arguments, build the map, write and print it."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("old_ref")
    parser.add_argument("new_ref")
    parser.add_argument("--overlay", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--category", help="restrict to one category directory")
    args = parser.parse_args()

    overlay: dict[str, Any] = {}
    if args.overlay and args.overlay.exists():
        overlay = json.loads(args.overlay.read_text(encoding="utf-8"))
    old = snapshot(args.old_ref, args.category)
    new = snapshot(args.new_ref, args.category)
    agents, problems = agent_rows(old["agents"], new["agents"], overlay)
    plugins = plugin_rows(old["plugins"], new["plugins"])
    doc = {
        "old_ref": args.old_ref,
        "old_commit": git("rev-parse", args.old_ref + "^{commit}").strip(),
        "new_ref": args.new_ref,
        "new_commit": git("rev-parse", args.new_ref + "^{commit}").strip(),
        "category": args.category,
        "overlay": str(args.overlay) if args.overlay else None,
        "summary": {
            "agents_old": len(old["agents"]),
            "agents_new": len(new["agents"]),
            "tree_fates": count(agents, "tree_fate"),
            "fates": count(agents, "fate"),
            "tools_change": count(agents, "tools_change"),
            "model_changed": sum(1 for r in agents if r["model_change"]),
            "plugins_old": len(old["plugins"]),
            "plugins_new": len(new["plugins"]),
            "plugin_dir_changed": sum(1 for p in plugins if "dir" in p["changed"]),
            "plugin_name_changed": sum(1 for p in plugins if "name" in p["changed"]),
            "plugin_version_changed": sum(1 for p in plugins if "version" in p["changed"]),
            "plugins_added": sum(1 for p in plugins if "added" in p["changed"]),
            "plugins_removed": sum(1 for p in plugins if "removed" in p["changed"]),
            "duplicate_names_old": old["duplicates"],
            "duplicate_names_new": new["duplicates"],
        },
        "marketplace": {"old": old["marketplace"], "new": new["marketplace"]},
        "overlay_problems": problems,
        "agents": agents,
        "plugins": plugins,
    }
    if args.out:
        args.out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    print_summary(doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
