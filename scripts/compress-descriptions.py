#!/usr/bin/env python3
"""Compress agent frontmatter ``description`` fields with a local Ollama model.

Rewriting an over-budget description to the CLAUDE.md "Description style"
(one sentence, at most 250 characters, task type first, then concrete
nouns; "Use proactively when..." only as the opening) is
mechanical: the output follows from the input with little judgement, so a
small local model does it instead of spending Claude tokens on it.

Two-phase workflow
------------------

1. Propose (default): read agent files, ask a local Ollama model to
rewrite each ``description:`` line, validate every candidate, and write
the results to a JSON report. The report is resumable: a file already
marked "proposed" is skipped on a later run unless ``--force`` is given;
a "failed" file is retried automatically. Nothing under ``categories/``
is touched in this phase.

2. Apply (``--apply``): re-read the report and rewrite ONLY the
``description:`` line of each file that has a valid ("proposed")
entry, leaving every other byte of the file identical. No Ollama call
happens in this phase.

Examples
--------

    # Propose compressed descriptions for every over-budget agent, using
    # the default model (qwen3-coder:30b), writing to
    # description-proposals.json:
    python scripts/compress-descriptions.py --over-budget

    # Same, but with the faster fallback model, and only the first 3 files:
    python scripts/compress-descriptions.py --over-budget \\
        --model gemma3:4b --limit 3

    # Review description-proposals.json by eye, then rewrite the files:
    python scripts/compress-descriptions.py --apply

    # Re-run generation for files already in the report:
    python scripts/compress-descriptions.py --over-budget --force
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_MODEL = "qwen3-coder:30b"
DEFAULT_HOST = "http://localhost:11434"  # DevSkim: ignore DS162092
DEFAULT_BUDGET = 250
DEFAULT_REPORT = "description-proposals.json"
DEFAULT_RETRIES = 2
DEFAULT_TIMEOUT = 300.0
DEFAULT_GLOB = "categories/*/*.md"
BODY_MAX_LINES = 40
BODY_MAX_CHARS = 3000
NUM_PREDICT = 200
TEMPERATURE = 0.1

DESCRIPTION_LINE_RE = re.compile(
    r'^(?P<prefix>\s*description:\s*)"(?P<value>.*)"[ \t]*$'
)
NAME_LINE_RE = re.compile(r"^\s*name:\s*(?P<value>.+?)\s*$")
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
# A sentence terminator followed by more text means there's a second
# sentence; a trailing one at the very end of the string does not match.
# Some of these are abbreviations rather than real sentence ends (see
# _is_abbreviation below).
MULTI_SENTENCE_RE = re.compile(r"[.!?]\s+\S")
# Abbreviations whose trailing period is not a sentence boundary. Dotted
# initialisms (e.g., i.e., U.S.) are caught by INITIALISM_RE instead.
ABBREVIATIONS = {"etc.", "vs.", "approx.", "incl."}
INITIALISM_RE = re.compile(r"^(?:[a-z]\.){2,}$")
# The style allows "Use proactively when..." only as the opening words.
PROACTIVE_PHRASE_RE = re.compile(r"(?i)\buse proactively\b")
PROACTIVE_PREFIX_RE = re.compile(r"(?i)^use proactively when\b")

STYLE_RULES = """You compress Claude Code agent frontmatter descriptions to a \
house style.

Rules for the rewritten description:
- Exactly one sentence, with a single terminal period. Never write a
second sentence.
- At most {budget} characters, total.
- Task type first (what kind of work this agent does), then the concrete
nouns a user would type: languages, tools, frameworks, file types,
commands.
- No marketing words ("expert", "world-class", "seamless", "cutting-edge",
"robust", "powerful", and similar).
- Preserve the meaning of the current description. Do not invent
capabilities that are not already there.
- Start with "Use proactively when ..." only if the current description
already says this agent should act without being asked; the rest of that
same sentence then says what it does. Never put "Use proactively" anywhere
but the very start, and leave it out entirely otherwise. "Use this agent
when ..." is NOT such a signal; drop that phrasing and lead with the task.
- Plain text only: no surrounding quotes, no markdown, no line breaks, no
<example> blocks.

Respond by calling the schema with a single "description" field."""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {"description": {"type": "string"}},
    "required": ["description"],
}


@dataclass
class ParsedAgent:
    """One agent file's frontmatter, as needed to propose or apply a rewrite."""

    path: Path
    lines: list[str]
    name: str
    description_value: str
    description_line_no: int
    description_prefix: str
    line_ending: str
    frontmatter_end: int


@dataclass
class GenerationConfig:
    """Ollama call parameters, grouped to keep function signatures short."""

    model: str
    host: str
    budget: int
    retries: int
    timeout: float


@dataclass
class Proposal:
    """The outcome of one propose() call, success or failure."""

    candidate: str | None
    escaped: str | None
    attempts: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


def unescape_double_quoted(value: str) -> str:
    """Decode the subset of YAML double-quoted escapes this catalog uses.

    >>> unescape_double_quoted('a \\\\"quoted\\\\" word')
    'a "quoted" word'
    >>> unescape_double_quoted('line one\\\\nline two')
    'line one\\nline two'
    """
    out: list[str] = []
    index = 0
    length = len(value)
    while index < length:
        char = value[index]
        if char == "\\" and index + 1 < length:
            nxt = value[index + 1]
            if nxt == "n":
                out.append("\n")
                index += 2
                continue
            if nxt == "t":
                out.append("\t")
                index += 2
                continue
            if nxt in ('"', "\\"):
                out.append(nxt)
                index += 2
                continue
        out.append(char)
        index += 1
    return "".join(out)


def escape_double_quoted(value: str) -> str:
    """Encode text for use inside a YAML double-quoted scalar.

    >>> escape_double_quoted('a "quoted" word')
    'a \\\\"quoted\\\\" word'
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def split_line_ending(line: str) -> tuple[str, str]:
    """Split a raw line into (body, ending), where ending is '', '\\n' or '\\r\\n'."""
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    if line.endswith("\r"):
        return line[:-1], "\r"
    return line, ""


def parse_agent_file(path: Path) -> ParsedAgent | None:
    """Parse an agent file's frontmatter, or return None if it has none."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        lines = handle.readlines()
    if not lines or split_line_ending(lines[0])[0] != "---":
        return None
    end_index = None
    for index in range(1, len(lines)):
        if split_line_ending(lines[index])[0] == "---":
            end_index = index
            break
    if end_index is None:
        return None

    name = None
    description_value = None
    description_line_no = None
    description_prefix = ""
    line_ending = "\n"
    for index in range(1, end_index):
        body, ending = split_line_ending(lines[index])
        name_match = NAME_LINE_RE.match(body)
        if name_match and name is None:
            name = name_match.group("value")
        description_match = DESCRIPTION_LINE_RE.match(body)
        if description_match:
            description_value = unescape_double_quoted(description_match.group("value"))
            description_line_no = index
            description_prefix = description_match.group("prefix")
            line_ending = ending or "\n"

    if name is None or description_line_no is None or description_value is None:
        return None
    return ParsedAgent(
        path=path,
        lines=lines,
        name=name,
        description_value=description_value,
        description_line_no=description_line_no,
        description_prefix=description_prefix,
        line_ending=line_ending,
        frontmatter_end=end_index,
    )


def body_excerpt(agent: ParsedAgent) -> str:
    """Return the role line plus the body's opening, capped for prompt size."""
    start = agent.frontmatter_end + 1
    end = start + BODY_MAX_LINES
    chunk = agent.lines[start:end]
    text = "".join(chunk).strip()
    if len(text) > BODY_MAX_CHARS:
        text = text[:BODY_MAX_CHARS]
    return text


def build_user_prompt(agent: ParsedAgent, budget: int) -> str:
    """Build the compact per-agent prompt: name, current description, body opening."""
    return (
        f"Agent name: {agent.name}\n"
        f"Current description: {agent.description_value}\n\n"
        "Opening of the agent's body, for context on what it actually does:\n"
        "---\n"
        f"{body_excerpt(agent)}\n"
        "---\n\n"
        f"Rewrite the description per the style rules, staying at or under "
        f"{budget} characters."
    )


def _is_abbreviation(text: str, period_index: int) -> bool:
    """True if the token ending at text[period_index] is a known abbreviation.

    >>> _is_abbreviation("tools e.g. print", 9)
    True
    >>> _is_abbreviation("the U.S. market", 7)
    True
    >>> _is_abbreviation("tools (e.g. print", 10)
    True
    >>> _is_abbreviation("Fixes bugs. Then ships", 10)
    False
    """
    start = period_index
    while start > 0 and not text[start - 1].isspace():
        start -= 1
    token = text[start : period_index + 1].lower().lstrip("([{\"'")
    return token in ABBREVIATIONS or bool(INITIALISM_RE.match(token))


def find_sentence_boundaries(text: str) -> list[int]:
    """Return indices of real sentence-ending punctuation in `text`.

    Skips punctuation that closes a known abbreviation (e.g., i.e., etc.,
    U.S.), which is not a sentence boundary.

    >>> find_sentence_boundaries("Fixes bugs using tools e.g. print statements.")
    []
    >>> find_sentence_boundaries("Fixes bugs. Then ships fixes.")
    [10]
    """
    boundaries = []
    for match in MULTI_SENTENCE_RE.finditer(text):
        period_index = match.start()
        if text[period_index] == "." and _is_abbreviation(text, period_index):
            continue
        boundaries.append(period_index)
    return boundaries


def has_extra_sentence(text: str) -> bool:
    """True if `text` has more than one sentence.

    >>> has_extra_sentence("Reviews pull requests for style issues.")
    False
    >>> has_extra_sentence("Reviews pull requests. Use proactively when a PR opens.")
    True
    """
    return bool(find_sentence_boundaries(text))


def has_misplaced_proactive(text: str) -> bool:
    """True if "Use proactively" appears anywhere but the very start.

    >>> has_misplaced_proactive("Use proactively when a PR opens to review it.")
    False
    >>> has_misplaced_proactive("Reviews PRs; use proactively when one opens.")
    True
    """
    match = PROACTIVE_PHRASE_RE.search(text)
    if match is None:
        return False
    return not (match.start() == 0 and PROACTIVE_PREFIX_RE.match(text))


def validate_candidate(
    candidate: str | None, original: str, budget: int
) -> tuple[str | None, list[str]]:
    """Validate a proposed description; return (escaped_value, reasons_if_invalid)."""
    reasons: list[str] = []
    if candidate is None:
        return None, ["model returned no description"]
    text = candidate.strip()
    if not text:
        return None, ["proposal is empty"]
    if "\n" in candidate or "\r" in candidate:
        reasons.append("proposal is not a single line")
    if CONTROL_CHAR_RE.search(candidate):
        reasons.append("proposal contains control characters")
    if len(text) > budget:
        reasons.append(f"proposal is {len(text)} characters, over the {budget} budget")
    if has_extra_sentence(text):
        reasons.append("looks like more than one sentence")
    if has_misplaced_proactive(text):
        reasons.append('"Use proactively when" may only open the description')
    if "<example" in text.lower():
        reasons.append("proposal contains an <example> block")
    if text == original.strip():
        reasons.append("proposal is identical to the original description")
    if reasons:
        return None, reasons
    return escape_double_quoted(text), []


def ollama_chat(
    host: str, model: str, messages: list[dict[str, str]], timeout: float
) -> dict[str, Any]:
    """Call Ollama's /api/chat with structured output and return the parsed reply."""
    parsed_host = urllib.parse.urlsplit(host)
    if parsed_host.scheme not in ("http", "https"):
        raise ValueError(f"unsupported host scheme: {host!r}")
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "format": RESPONSE_SCHEMA,
        "options": {"temperature": TEMPERATURE, "num_predict": NUM_PREDICT},
    }
    request = urllib.request.Request(
        f"{host.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    # The host is a fixed local Ollama endpoint (default localhost, or an
    # explicit --host flag); scheme is checked above. nosec: B310
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
        raw = response.read()
    return json.loads(raw)


def propose_description(agent: ParsedAgent, config: GenerationConfig) -> Proposal:
    """Ask Ollama for a compressed description, retrying on validation failure."""
    messages = [
        {"role": "system", "content": STYLE_RULES.format(budget=config.budget)},
        {"role": "user", "content": build_user_prompt(agent, config.budget)},
    ]
    attempts: list[dict[str, Any]] = []
    last_error = "unknown error"

    for attempt in range(1, config.retries + 2):
        try:
            reply = ollama_chat(config.host, config.model, messages, config.timeout)
            content = json.loads(reply["message"]["content"])
            candidate = content.get("description")
        except (
            urllib.error.URLError,
            OSError,
            TimeoutError,
            json.JSONDecodeError,
            KeyError,
            ValueError,
        ) as exc:
            last_error = f"request failed: {exc}"
            attempts.append({"attempt": attempt, "error": last_error})
            messages.append(
                {
                    "role": "user",
                    "content": f"That failed ({last_error}). Retry with valid JSON.",
                }
            )
            continue

        escaped, reasons = validate_candidate(
            candidate, agent.description_value, config.budget
        )
        if not reasons:
            attempts.append({"attempt": attempt, "candidate": candidate, "ok": True})
            return Proposal(
                candidate=candidate.strip(), escaped=escaped, attempts=attempts
            )

        last_error = "; ".join(reasons)
        attempts.append(
            {"attempt": attempt, "candidate": candidate, "error": last_error}
        )
        messages.append({"role": "assistant", "content": json.dumps(content)})
        messages.append(
            {
                "role": "user",
                "content": (
                    f"That description is invalid: {last_error}. Fix it: exactly "
                    f"one sentence, no line breaks, at most {config.budget} "
                    "characters."
                ),
            }
        )

    return Proposal(candidate=None, escaped=None, attempts=attempts, error=last_error)


def to_key(path: Path) -> str:
    """A portable, forward-slash report key for a file path."""
    return path.as_posix()


def collect_files(patterns: list[str]) -> list[Path]:
    """Expand CLI positional arguments (files, directories, globs) to agent files."""
    if not patterns:
        patterns = [DEFAULT_GLOB]
    result: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        candidate_path = Path(pattern)
        if candidate_path.is_dir():
            found: list[Path] = sorted(candidate_path.glob("*.md"))
        elif candidate_path.is_file():
            found = [candidate_path]
        else:
            found = sorted(Path(match) for match in glob.glob(pattern, recursive=True))
        for item in found:
            if item.name == "README.md":
                continue
            resolved = item.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            result.append(item)
    return result


def load_report(report_path: Path) -> dict[str, Any]:
    """Load the JSON report, or an empty dict if it does not exist yet."""
    if report_path.exists():
        with report_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}


def save_report(report_path: Path, report: dict[str, Any]) -> None:
    """Write the report atomically so an interrupted run leaves valid JSON."""
    tmp_path = report_path.with_name(report_path.name + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(report_path)


def collect_candidates(
    args: argparse.Namespace, report: dict[str, Any]
) -> tuple[list[tuple[str, ParsedAgent]], list[str]]:
    """Pick files to propose for: parseable, over-budget if asked, not already done.

    Returns the candidates and the keys of files that could not be parsed.
    """
    candidates: list[tuple[str, ParsedAgent]] = []
    unparseable: list[str] = []
    for file_path in collect_files(args.paths):
        agent = parse_agent_file(file_path)
        if agent is None:
            unparseable.append(to_key(file_path))
            continue
        if args.over_budget and len(agent.description_value) <= args.budget:
            continue
        key = to_key(file_path)
        already_proposed = report.get(key, {}).get("status") == "proposed"
        if already_proposed and not args.force:
            continue
        candidates.append((key, agent))
    if args.limit is not None:
        candidates = candidates[: args.limit]
    return candidates, unparseable


def run_propose(args: argparse.Namespace) -> int:
    """Propose phase: call Ollama for each candidate file and write the report."""
    config = GenerationConfig(
        model=args.model,
        host=args.host,
        budget=args.budget,
        retries=args.retries,
        timeout=args.timeout,
    )
    report = load_report(args.report)
    candidates, unparseable = collect_candidates(args, report)

    for key in unparseable:
        print(
            f"skip {key}: no frontmatter with a name and a one-line "
            'double-quoted description: "..."',
            file=sys.stderr,
        )
    total = len(candidates)
    print(
        f"Proposing descriptions for {total} file(s) with {args.model} at "
        f"{args.host}; {len(unparseable)} unparseable file(s) skipped",
        file=sys.stderr,
    )
    for position, (key, agent) in enumerate(candidates, start=1):
        started = time.monotonic()
        print(
            f"[{position}/{total}] {key}: requesting {args.model} ...", file=sys.stderr
        )
        result = propose_description(agent, config)
        elapsed = time.monotonic() - started
        entry: dict[str, Any] = {
            "name": agent.name,
            "original": agent.description_value,
            "model": args.model,
            "budget": args.budget,
            "elapsed_seconds": round(elapsed, 2),
            "attempts": result.attempts,
        }
        if result.candidate is not None:
            entry["status"] = "proposed"
            entry["proposed"] = result.candidate
            print(
                f"[{position}/{total}] {key}: ok in {elapsed:.1f}s "
                f"({len(result.candidate)} chars)",
                file=sys.stderr,
            )
        else:
            entry["status"] = "failed"
            entry["error"] = result.error
            print(
                f"[{position}/{total}] {key}: FAILED in {elapsed:.1f}s "
                f"({result.error})",
                file=sys.stderr,
            )
        report[key] = entry
        save_report(args.report, report)

    return 0


def run_apply(args: argparse.Namespace) -> int:
    """Apply phase: rewrite only the description line of each proposed file."""
    report = load_report(args.report)
    if not report:
        print(
            f"No report at {args.report}; run the propose phase first.", file=sys.stderr
        )
        return 1

    applied = 0
    skipped = 0
    for key, entry in sorted(report.items()):
        if entry.get("status") != "proposed":
            continue
        file_path = Path(key)
        if not file_path.exists():
            print(f"skip {key}: file no longer exists", file=sys.stderr)
            skipped += 1
            continue
        agent = parse_agent_file(file_path)
        if agent is None:
            print(f"skip {key}: could not re-parse frontmatter", file=sys.stderr)
            skipped += 1
            continue
        if entry.get("original") != agent.description_value:
            print(f"skip {key}: source file changed since proposal", file=sys.stderr)
            skipped += 1
            continue
        budget = entry.get("budget", args.budget)
        escaped, reasons = validate_candidate(
            entry.get("proposed"), agent.description_value, budget
        )
        if reasons:
            print(
                f"skip {key}: re-validation failed ({'; '.join(reasons)})",
                file=sys.stderr,
            )
            skipped += 1
            continue
        new_line = f'{agent.description_prefix}"{escaped}"{agent.line_ending}'
        agent.lines[agent.description_line_no] = new_line
        with file_path.open("w", encoding="utf-8", newline="") as handle:
            handle.writelines(agent.lines)
        applied += 1
        print(f"applied {key}", file=sys.stderr)

    print(f"Applied {applied} file(s); skipped {skipped}.", file=sys.stderr)
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI parser, with --help documenting the two-phase workflow."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help=f"Agent files, directories or globs (default: {DEFAULT_GLOB}).",
    )
    parser.add_argument(
        "--over-budget",
        action="store_true",
        help="Only propose for descriptions currently longer than --budget.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Ollama model tag to use (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Ollama server URL (default: {DEFAULT_HOST}).",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=DEFAULT_BUDGET,
        help=f"Maximum description length in characters (default: {DEFAULT_BUDGET}).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(DEFAULT_REPORT),
        help=f"JSON report, read/written by both phases (default: {DEFAULT_REPORT}).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply phase: rewrite description lines from the report; no Ollama call.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Propose phase: re-propose files already marked 'proposed' (a "
        "'failed' entry is retried automatically, without this flag).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Propose phase: process at most N files this run.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help=f"Extra attempts after a validation failure (default: {DEFAULT_RETRIES}).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"HTTP timeout per Ollama call, in seconds (default: {DEFAULT_TIMEOUT}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point: dispatch to the propose or apply phase."""
    args = build_arg_parser().parse_args(argv)
    if args.apply:
        return run_apply(args)
    return run_propose(args)


if __name__ == "__main__":
    sys.exit(main())
