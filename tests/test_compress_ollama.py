"""compress-descriptions.py against a real local Ollama server.

tests/test_compress_descriptions.py fakes Ollama, so it assumes the shape of
an /api/chat reply and that the JSON schema sent in "format" comes back as a
"description" field. These tests check those assumptions against the real
thing. They don't judge the model's wording: a human reviews every proposal
before --apply, by design.

Deselected by default (pyproject.toml), and skipped when no server answers:

    python3 -m pytest -m ollama
    OLLAMA_TEST_MODEL=qwen3-coder:30b python3 -m pytest -m ollama
"""

# pylint: disable=missing-function-docstring

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import pytest
from builders import load_compress_descriptions

cd = load_compress_descriptions()

HOST = os.environ.get("OLLAMA_HOST", cd.DEFAULT_HOST)
MODEL = os.environ.get("OLLAMA_TEST_MODEL", "gemma3:4b")
TIMEOUT = 600.0  # small local models are slow

pytestmark = pytest.mark.ollama


def installed_models() -> list[str] | None:
    """Model names the server has, or None when no server answers."""
    if urllib.parse.urlsplit(HOST).scheme not in ("http", "https"):
        return None
    try:
        # Scheme checked above, as ollama_chat() checks it.
        url = f"{HOST}/api/tags"
        with urllib.request.urlopen(url, timeout=3) as response:  # nosec B310
            tags: dict[str, Any] = json.load(response)
    except (urllib.error.URLError, OSError):
        return None
    return [m["name"] for m in tags.get("models", [])]


@pytest.fixture(name="model", scope="module")
def model_fixture() -> str:
    models = installed_models()
    if models is None:
        pytest.skip(f"no Ollama server at {HOST}")
    if MODEL not in models:
        pytest.skip(f"{MODEL} not installed; set OLLAMA_TEST_MODEL")
    return MODEL


AGENT = """---
name: pr-reviewer
description: "Use this agent when you need a world-class expert to review pull \
requests for style, naming and structure. It also comments on tests and docs."
tools: Read, Grep
---

You are a pull request reviewer. You read diffs and report style, naming and
structure problems, with file and line references.
"""


def test_reply_has_the_shape_the_script_parses(model: str) -> None:
    messages = [
        {"role": "system", "content": cd.STYLE_RULES.format(budget=120)},
        {"role": "user", "content": "Describe an agent that reviews pull requests."},
    ]
    reply = cd.ollama_chat(HOST, model, messages, TIMEOUT)
    # What propose_description() reads: reply["message"]["content"] is JSON
    # text whose "description" is a string, as RESPONSE_SCHEMA asks.
    content = json.loads(reply["message"]["content"])
    assert isinstance(content, dict)
    assert isinstance(content.get("description"), str)


def test_propose_then_apply_with_a_real_model(model: str, tmp_path: Path) -> None:
    agent_file = tmp_path / "pr-reviewer.md"
    agent_file.write_text(AGENT, encoding="utf-8", newline="\n")
    report = tmp_path / "report.json"
    argv = [str(agent_file), "--model", model, "--host", HOST]
    argv += ["--report", str(report), "--timeout", str(TIMEOUT)]

    assert cd.main(argv) == 0
    entry = cd.load_report(report)[cd.to_key(agent_file)]
    assert_no_request_errors(entry)
    if entry["status"] != "proposed":
        pytest.skip(f"{model} produced no valid description: {entry['error']}")

    assert cd.main(["--apply", "--report", str(report)]) == 0
    assert changed_lines(AGENT, agent_file.read_text(encoding="utf-8")) == [2]
    assert cd.parse_agent_file(agent_file).description_value == entry["proposed"]


def assert_no_request_errors(entry: dict[str, Any]) -> None:
    """Every attempt reached the model and got a parseable reply.

    The model may fail validation on every retry; that is a legitimate
    outcome the report records, not a broken pipeline. A request error is.
    """
    assert entry["attempts"], "no attempt recorded"
    for attempt in entry["attempts"]:
        assert not attempt.get("error", "").startswith("request failed"), attempt


def changed_lines(before: str, after: str) -> list[int]:
    """Indexes of the lines that differ; the line count must not change."""
    pairs = zip(before.splitlines(), after.splitlines(), strict=True)
    return [i for i, (a, b) in enumerate(pairs) if a != b]
