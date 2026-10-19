import json
from pathlib import Path

import pytest

from paper_review.llm.command_code import (
    CommandCodeRunner,
    build_cmd_argv,
    parse_cmd_stdout,
    parse_json_object,
)
from paper_review.llm.base import LLMError
from paper_review.llm.mock import MockRunner
from paper_review.llm.flow import copy_from_obj, critique_from_obj, facts_from_obj
from paper_review.models import Critique, ExtractFacts, Figure


def test_argv_matches_docs():
    argv = build_cmd_argv("hello world", "deepseek/deepseek-v4-flash", 3)
    assert argv[0] == "cmd"
    assert argv[1] == "-t"
    assert argv[2] == "-p"
    assert argv[3] == "hello world"
    assert argv[4] == "-m"
    assert argv[5] == "deepseek/deepseek-v4-flash"
    assert "--max-turns" in argv
    assert argv[argv.index("--max-turns") + 1] == "3"
    assert "--output-format" in argv
    assert argv[argv.index("--output-format") + 1] == "json"
    assert "--skip-onboarding" in argv


def test_parse_ndjson_success():
    stdout = "\n".join(
        [
            json.dumps({"type": "event", "event": {"type": "tool_running", "toolName": "read_file"}}),
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "sessionId": "abc",
                    "stopReason": "end_turn",
                    "usage": {},
                    "durationMs": 12,
                    "finalText": '{"ok": true}',
                }
            ),
        ]
    )
    assert parse_cmd_stdout(stdout) == '{"ok": true}'


def test_parse_error_result_does_not_require_session():
    stdout = json.dumps({"type": "result", "subtype": "error", "error": "auth failed", "finalText": "", "usage": {}, "durationMs": 1})
    with pytest.raises(LLMError, match="auth failed"):
        parse_cmd_stdout(stdout)


def test_parse_max_turns_empty():
    stdout = json.dumps({"type": "result", "subtype": "max_turns", "finalText": "", "usage": {}, "durationMs": 1})
    with pytest.raises(LLMError, match="max turns"):
        parse_cmd_stdout(stdout)


def test_parse_text_fallback():
    assert parse_cmd_stdout("just a paragraph") == "just a paragraph"


def test_parse_json_object_fences():
    obj = parse_json_object("```json\n{\"a\": 1}\n```")
    assert obj == {"a": 1}


def test_runner_requires_api_key(tmp_path: Path, monkeypatch):
    fake = tmp_path / "cmd"
    fake.write_text("#!/bin/sh\nexit 0\n")
    fake.chmod(0o755)
    monkeypatch.delenv("COMMAND_CODE_API_KEY", raising=False)
    runner = CommandCodeRunner(bin_name=str(fake))
    with pytest.raises(LLMError, match="COMMAND_CODE_API_KEY"):
        runner.complete("hi")


def test_runner_invokes_cli(tmp_path: Path, monkeypatch):
    script = tmp_path / "cmd"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "print(json.dumps({'type':'result','subtype':'success','finalText':'pong','usage':{},'durationMs':1}))\n"
    )
    script.chmod(0o755)
    monkeypatch.setenv("COMMAND_CODE_API_KEY", "test-key")
    runner = CommandCodeRunner(bin_name=str(script), env={"COMMAND_CODE_API_KEY": "test-key"})
    assert runner.complete("ping") == "pong"


def test_mock_extract_json_roundtrip():
    fig = Figure("fig-1", "Figure 1: Overview of the pipeline.", "u", "fig-1.png", "p", index=1)
    runner = MockRunner()
    prompt = (
        "TITLE: Waypoint-OPD: Gated Distillation\n"
        "ABSTRACT: We introduce Waypoint-OPD. On MathBench it scores 71.2% versus 64.0% for the baseline.\n"
        "FIGURE CATALOG (allow-listed ids only):\n"
        "- fig-1 [Figure 1]: Figure 1: Overview of the pipeline.\n"
        "PAPER TEXT: method details\n"
    )
    obj = parse_json_object(runner.complete(prompt))
    facts = facts_from_obj(obj, [fig])
    assert facts.method_figure_id == "fig-1"
    crit = critique_from_obj(parse_json_object(runner.complete(
        "You are a skeptical but fair reviewer.\nTITLE: Waypoint-OPD\nEXTRACTED FACTS:\n71.2%\n"
    )))
    assert crit.support_strength in {"strong", "moderate", "weak"}
    copy = copy_from_obj(
        parse_json_object(runner.complete(
            "Write a methodology card in plain English.\nTITLE: Waypoint-OPD\n"
            "FACTS: gated distillation\nResults: 71.2%\nCRITIQUE caveat: be careful\n"
            "FIGURES:\n- fig-1 [Figure 1]: Figure 1: Overview of the pipeline.\n"
        )),
        facts,
        Critique("moderate", "c", "be careful"),
        [fig],
    )
    assert copy.core_method
    assert copy.method_figure_id == "fig-1"


def test_rejects_unknown_figure_id():
    fig = Figure("fig-1", "cap", "u", "f", "p", index=1)
    facts = facts_from_obj({"problem": "p", "core_method": "m", "method_figure_id": "fig-99"}, [fig])
    assert facts.method_figure_id is None


def test_parse_json_object_trailing_commas():
    obj = parse_json_object('{"a": 1, "b": [2, 3,],}')
    assert obj == {"a": 1, "b": [2, 3]}


def test_parse_json_object_smart_quotes():
    obj = parse_json_object("{“problem”: “hello”, “n”: 1}")
    assert obj["problem"] == "hello"
    assert obj["n"] == 1


def test_parse_json_object_embedded_in_prose():
    text = "Sure, here is the result:\n\n{\"ok\": true, \"score\": 3}\n\nHope that helps!"
    obj = parse_json_object(text)
    assert obj == {"ok": True, "score": 3}


def test_parse_json_object_balanced_ignores_trailing_junk():
    # Extra closing braces / prose after a valid object should still parse.
    text = '''Here you go:
```json
{"a": 1, "b": "x"}
```
And some trailing notes with } braces that should be ignored.
'''
    obj = parse_json_object(text)
    assert obj == {"a": 1, "b": "x"}


def test_parse_json_object_rejects_non_object():
    with pytest.raises(LLMError):
        parse_json_object("[1, 2, 3]")
