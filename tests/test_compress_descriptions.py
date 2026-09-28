"""Behaviour of scripts/compress-descriptions.py, with Ollama faked out.

Nothing here talks to a model: ollama_chat() is replaced by a script of
canned replies, or urlopen() by a fake server, so the tests pin what the
script does with a reply, not what a model says.
"""

# Test names say what each test checks, and `== []` shows the unexpected
# items in pytest's failure diff where `not ...` would not.
# pylint: disable=missing-function-docstring
# pylint: disable=use-implicit-booleaness-not-comparison

from __future__ import annotations

import argparse
import doctest
import importlib.util
import io
import json
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load() -> ModuleType:
    """Import the script, whose hyphenated name can't be imported directly."""
    path = ROOT / "scripts" / "compress-descriptions.py"
    spec = importlib.util.spec_from_file_location("compress_descriptions", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cd = _load()

LONG = (
    "Use this agent when you need a world-class expert to review pull requests "
    "for style, naming and structure. It also comments on tests."
)


def agent_text(
    description: str = LONG, eol: str = "\n", name: str = "pr-reviewer"
) -> str:
    lines = [
        "---",
        f"name: {name}",
        f'description: "{description}"',
        "tools: Read, Grep",
        "---",
        "",
        "You are a pull request reviewer.",
    ]
    return eol.join(lines) + eol


def write(path: Path, text: str) -> Path:
    path.write_bytes(text.encode("utf-8"))
    return path


def chat_reply(description: str | None) -> dict[str, Any]:
    """An Ollama /api/chat reply whose structured content holds description."""
    content = {} if description is None else {"description": description}
    return {"message": {"content": json.dumps(content)}}


FakeChat = Callable[[str, str, list[dict[str, str]], float], dict[str, Any]]


def scripted_chat(*replies: dict[str, Any] | Exception) -> tuple[FakeChat, list[Any]]:
    """A stand-in for ollama_chat() that plays replies in order.

    Returns it and a list recording a copy of the messages of each call.
    """
    queue: Iterator[dict[str, Any] | Exception] = iter(replies)
    calls: list[Any] = []

    def fake(
        _host: str, _model: str, messages: list[dict[str, str]], _timeout: float
    ) -> dict[str, Any]:
        calls.append(list(messages))
        reply = next(queue)
        if isinstance(reply, Exception):
            raise reply
        return reply

    return fake, calls


def config(retries: int = 2, budget: int = 120) -> Any:
    return cd.GenerationConfig(
        model="test-model",
        host="http://localhost:11434",
        budget=budget,
        retries=retries,
        timeout=1.0,
    )


# -- Doctests and small helpers -----------------------------------------------


def test_doctests_pass() -> None:
    result = doctest.testmod(cd)
    assert result.attempted > 0
    assert result.failed == 0


@pytest.mark.parametrize(
    "text",
    ["plain", 'a "quoted" word', "back\\slash", 'both \\ and "'],
)
def test_escape_then_unescape_round_trips(text: str) -> None:
    assert cd.unescape_double_quoted(cd.escape_double_quoted(text)) == text


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("a\r\n", ("a", "\r\n")),
        ("a\n", ("a", "\n")),
        ("a\r", ("a", "\r")),
        ("a", ("a", "")),
    ],
)
def test_split_line_ending(line: str, expected: tuple[str, str]) -> None:
    assert cd.split_line_ending(line) == expected


# -- Parsing --------------------------------------------------------------------


def test_parse_agent_file(tmp_path: Path) -> None:
    agent = cd.parse_agent_file(write(tmp_path / "a.md", agent_text('Say \\"hi\\".')))
    assert agent is not None
    assert (agent.name, agent.description_value) == ("pr-reviewer", 'Say "hi".')
    assert (agent.description_line_no, agent.frontmatter_end) == (2, 4)
    assert (agent.description_prefix, agent.line_ending) == ("description: ", "\n")


def test_parse_keeps_crlf_line_ending(tmp_path: Path) -> None:
    agent = cd.parse_agent_file(write(tmp_path / "a.md", agent_text(eol="\r\n")))
    assert agent is not None
    assert agent.line_ending == "\r\n"


@pytest.mark.parametrize(
    "text",
    [
        "no frontmatter\n",
        "---\nname: x\n",  # never closed
        '---\ndescription: "d"\n---\n',  # no name
        "---\nname: x\ndescription: unquoted\n---\n",  # not double-quoted
    ],
)
def test_parse_rejects(tmp_path: Path, text: str) -> None:
    assert cd.parse_agent_file(write(tmp_path / "a.md", text)) is None


def test_parse_last_description_wins(tmp_path: Path) -> None:
    text = '---\nname: x\ndescription: "first"\ndescription: "second"\n---\n'
    agent = cd.parse_agent_file(write(tmp_path / "a.md", text))
    assert agent is not None
    assert (agent.description_value, agent.description_line_no) == ("second", 3)


def test_body_excerpt_is_capped(tmp_path: Path) -> None:
    text = agent_text() + ("x" * 100 + "\n") * 60
    agent = cd.parse_agent_file(write(tmp_path / "a.md", text))
    assert agent is not None
    excerpt = cd.body_excerpt(agent)
    assert excerpt.startswith("You are a pull request reviewer.")
    assert len(excerpt) <= cd.BODY_MAX_CHARS


def test_user_prompt_carries_name_description_and_budget(tmp_path: Path) -> None:
    agent = cd.parse_agent_file(write(tmp_path / "a.md", agent_text()))
    prompt = cd.build_user_prompt(agent, 99)
    assert "Agent name: pr-reviewer" in prompt
    assert LONG in prompt
    assert "99 characters" in prompt


# -- Validating a candidate -----------------------------------------------------


@pytest.mark.parametrize(
    ("candidate", "reason"),
    [
        (None, "model returned no description"),
        ("   ", "proposal is empty"),
        ("Reviews PRs\nfor style.", "proposal is not a single line"),
        ("Reviews PRs\x07.", "proposal contains control characters"),
        ("x" * 121, "proposal is 121 characters, over the 120 budget"),
        ("Reviews PRs. Also tests.", "looks like more than one sentence"),
        (
            "Reviews PRs; use proactively when one opens.",
            '"Use proactively when" may only open the description',
        ),
        ("Reviews <example> PRs.", "proposal contains an <example> block"),
        ("  The original.  ", "proposal is identical to the original description"),
    ],
)
def test_validate_candidate_rejects(candidate: str | None, reason: str) -> None:
    escaped, reasons = cd.validate_candidate(candidate, "The original.", 120)
    assert escaped is None
    assert reasons == [reason]


def test_validate_candidate_reports_every_reason_in_order() -> None:
    _, reasons = cd.validate_candidate("A. B <example>", "orig", 3)
    assert reasons == [
        "proposal is 14 characters, over the 3 budget",
        "looks like more than one sentence",
        "proposal contains an <example> block",
    ]


@pytest.mark.parametrize(
    "candidate",
    [
        "Reviews pull requests for style, e.g. naming, in the U.S. office.",
        "Use proactively when a PR opens to review its style.",
    ],
)
def test_validate_candidate_accepts(candidate: str) -> None:
    assert cd.validate_candidate(candidate, "orig", 120) == (candidate, [])


def test_validate_candidate_strips_and_escapes() -> None:
    assert cd.validate_candidate('  Say "hi".  ', "orig", 120) == ('Say \\"hi\\".', [])


# -- Talking to Ollama -----------------------------------------------------------


class FakeResponse(io.BytesIO):
    """What urlopen() returns, as a context manager."""

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def test_ollama_chat_request(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}

    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        seen.update(
            url=request.full_url, body=json.loads(request.data), timeout=timeout
        )
        return FakeResponse(json.dumps(chat_reply("ok")).encode())

    monkeypatch.setattr(cd.urllib.request, "urlopen", fake_urlopen)
    messages = [{"role": "user", "content": "hi"}]
    reply = cd.ollama_chat("http://localhost:11434/", "m", messages, 5.0)
    assert reply == chat_reply("ok")
    assert seen["url"] == "http://localhost:11434/api/chat"
    assert seen["timeout"] == 5.0
    body = seen["body"]
    assert (body["model"], body["messages"], body["stream"]) == ("m", messages, False)
    assert body["format"] == cd.RESPONSE_SCHEMA


@pytest.mark.parametrize(
    "host", ["file:///etc/passwd", "ftp://host", "localhost:11434"]
)
def test_ollama_chat_refuses_non_http_hosts(host: str) -> None:
    with pytest.raises(ValueError, match="unsupported host scheme"):
        cd.ollama_chat(host, "m", [], 1.0)


# -- Proposing, with retries -------------------------------------------------------


@pytest.fixture(name="agent")
def agent_fixture(tmp_path: Path) -> Any:
    return cd.parse_agent_file(write(tmp_path / "pr-reviewer.md", agent_text()))


def test_propose_first_try(monkeypatch: pytest.MonkeyPatch, agent: Any) -> None:
    fake, calls = scripted_chat(chat_reply("  Reviews PRs for style.  "))
    monkeypatch.setattr(cd, "ollama_chat", fake)
    result = cd.propose_description(agent, config())
    assert (result.candidate, result.escaped, result.error) == (
        "Reviews PRs for style.",
        "Reviews PRs for style.",
        None,
    )
    assert len(calls) == 1
    assert [m["role"] for m in calls[0]] == ["system", "user"]
    assert "120 characters" in calls[0][0]["content"]


def test_propose_feeds_the_reason_back_and_retries(
    monkeypatch: pytest.MonkeyPatch, agent: Any
) -> None:
    fake, calls = scripted_chat(
        chat_reply("Reviews PRs. Also tests."),
        chat_reply("Reviews PRs and tests for style."),
    )
    monkeypatch.setattr(cd, "ollama_chat", fake)
    result = cd.propose_description(agent, config())
    assert result.candidate == "Reviews PRs and tests for style."
    assert [a.get("ok", False) for a in result.attempts] == [False, True]
    retry = calls[1]
    assert retry[-2] == {
        "role": "assistant",
        "content": json.dumps({"description": "Reviews PRs. Also tests."}),
    }
    assert "looks like more than one sentence" in retry[-1]["content"]


def test_propose_retries_request_and_reply_errors(
    monkeypatch: pytest.MonkeyPatch, agent: Any
) -> None:
    fake, _ = scripted_chat(
        OSError("connection refused"),
        {"message": {"content": "not json"}},
        chat_reply("Reviews PRs for style."),
    )
    monkeypatch.setattr(cd, "ollama_chat", fake)
    result = cd.propose_description(agent, config(retries=2))
    assert result.candidate == "Reviews PRs for style."
    assert result.attempts[0]["error"] == "request failed: connection refused"
    assert result.attempts[1]["error"].startswith("request failed: Expecting value")


def test_propose_gives_up_after_the_retries(
    monkeypatch: pytest.MonkeyPatch, agent: Any
) -> None:
    fake, calls = scripted_chat(*[chat_reply(None)] * 3)
    monkeypatch.setattr(cd, "ollama_chat", fake)
    result = cd.propose_description(agent, config(retries=2))
    assert (result.candidate, result.escaped) == (None, None)
    assert result.error == "model returned no description"
    assert len(calls) == len(result.attempts) == 3


# -- Files and the report ----------------------------------------------------------


def test_collect_files(tmp_path: Path) -> None:
    cat = tmp_path / "categories" / "01-x"
    cat.mkdir(parents=True)
    a = write(cat / "a.md", agent_text())
    b = write(cat / "b.md", agent_text())
    write(cat / "README.md", "# readme\n")
    files = cd.collect_files([str(cat), str(a), str(cat / "*.md")])
    assert files == [a, b]  # README dropped, a not repeated


def test_report_round_trips_and_leaves_no_temp_file(tmp_path: Path) -> None:
    path = tmp_path / "report.json"
    assert cd.load_report(path) == {}
    cd.save_report(path, {"k": {"status": "proposed"}})
    assert cd.load_report(path) == {"k": {"status": "proposed"}}
    assert path.read_bytes().endswith(b"}\n")
    assert list(tmp_path.iterdir()) == [path]


def args_for(tmp_path: Path, *argv: str) -> argparse.Namespace:
    parsed: argparse.Namespace = cd.build_arg_parser().parse_args(
        [*argv, "--report", str(tmp_path / "report.json")]
    )
    return parsed


def test_collect_candidates(tmp_path: Path) -> None:
    short = write(tmp_path / "short.md", agent_text("Reviews PRs."))
    long_done = write(tmp_path / "done.md", agent_text())
    long_failed = write(tmp_path / "failed.md", agent_text())
    broken = write(tmp_path / "broken.md", "no frontmatter\n")
    report = {
        cd.to_key(long_done): {"status": "proposed"},
        cd.to_key(long_failed): {"status": "failed"},
    }
    paths = [str(p) for p in (short, long_done, long_failed, broken)]

    args = args_for(tmp_path, "--over-budget", "--budget", "50", *paths)
    candidates, unparseable = cd.collect_candidates(args, report)
    assert [k for k, _ in candidates] == [cd.to_key(long_failed)]
    assert unparseable == [cd.to_key(broken)]

    forced = args_for(tmp_path, "--over-budget", "--budget", "50", "--force", *paths)
    candidates, _ = cd.collect_candidates(forced, report)
    assert [k for k, _ in candidates] == [cd.to_key(long_done), cd.to_key(long_failed)]

    limited = args_for(tmp_path, "--limit", "1", *paths)
    candidates, _ = cd.collect_candidates(limited, report)
    assert [k for k, _ in candidates] == [cd.to_key(short)]


# -- The two phases end to end --------------------------------------------------------


def test_propose_then_apply_changes_only_the_description_line(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    original = agent_text(eol="\r\n")
    ok = write(tmp_path / "ok.md", original)
    bad = write(tmp_path / "bad.md", agent_text(name="bad"))
    fake, _ = scripted_chat(
        chat_reply(None),  # bad.md, given first: three failures
        chat_reply(None),
        chat_reply(None),
        chat_reply('Reviews PRs for "style".'),  # ok.md
    )
    monkeypatch.setattr(cd, "ollama_chat", fake)

    assert cd.main([str(bad), str(ok), "--report", str(tmp_path / "r.json")]) == 0
    report = cd.load_report(tmp_path / "r.json")
    assert report[cd.to_key(ok)]["status"] == "proposed"
    assert report[cd.to_key(bad)]["status"] == "failed"
    assert ok.read_bytes() == original.encode()  # propose touches no agent file

    assert cd.main(["--apply", "--report", str(tmp_path / "r.json")]) == 0
    expected = original.replace(f'"{LONG}"', '"Reviews PRs for \\"style\\"."')
    assert ok.read_bytes() == expected.encode()  # CRLF and every other byte kept
    assert bad.read_bytes() == agent_text(name="bad").encode()


def test_apply_skips_what_it_cannot_trust(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    changed = write(tmp_path / "changed.md", agent_text("Edited since."))
    invalid = write(tmp_path / "invalid.md", agent_text())
    report = {
        cd.to_key(tmp_path / "gone.md"): {"status": "proposed", "original": LONG},
        cd.to_key(changed): {"status": "proposed", "original": LONG, "proposed": "X."},
        cd.to_key(invalid): {
            "status": "proposed",
            "original": LONG,
            "proposed": "A. B.",
        },
    }
    cd.save_report(tmp_path / "r.json", report)
    assert cd.main(["--apply", "--report", str(tmp_path / "r.json")]) == 0
    err = capsys.readouterr().err
    assert "file no longer exists" in err
    assert "source file changed since proposal" in err
    assert "re-validation failed (looks like more than one sentence)" in err
    assert "Applied 0 file(s); skipped 3." in err
    assert invalid.read_bytes() == agent_text().encode()


def test_apply_without_a_report_fails(tmp_path: Path) -> None:
    assert cd.main(["--apply", "--report", str(tmp_path / "none.json")]) == 1
