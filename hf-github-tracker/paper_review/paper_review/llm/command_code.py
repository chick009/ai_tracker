"""Command Code CLI runner.

CLI contract (https://commandcode.ai/docs/headless,
https://commandcode.ai/docs/reference/cli):

    cmd -t -p "<prompt>" -m deepseek/deepseek-v4-flash --max-turns N --output-format json

Auth: COMMAND_CODE_API_KEY is read by the CLI at startup and overrides
~/.commandcode/auth.json (https://commandcode.ai/docs/studio).
JSON stdout is NDJSON: event frames, then one final `{"type":"result",...}`
line whose `finalText` is the answer.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
from typing import Any

from paper_review.config import CMD_BIN, DEFAULT_MODEL
from paper_review.llm.base import LLMError, LLMRunner

log = logging.getLogger("paper_review")

# Headless exit codes from the Command Code docs.
EXIT_MAX_TURNS = 8
EXIT_NO_RESPONSE = 9
EXIT_AUTH = 3
EXIT_CREDITS = 10

_SMART_QUOTES = str.maketrans({
    "\u201c": '"',  # “
    "\u201d": '"',  # ”
    "\u2018": "'",  # ‘
    "\u2019": "'",  # ’
    "\u00ab": '"',  # «
    "\u00bb": '"',  # »
    "\uff02": '"',  # ＂
    "\u201e": '"',  # „
    "\u2033": '"',  # ″
})


def build_cmd_argv(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_turns: int = 4,
    *,
    output_format: str = "json",
    bin_name: str = CMD_BIN,
) -> list[str]:
    """Exact argv for a headless Command Code completion.

    `-t` auto-trusts the working directory (skips the first-run prompt).
    `-p` is print/headless mode. `--skip-onboarding` is the CI-safe path.
    `--no-session` keeps daily pipeline runs from polluting session history.
    """
    argv = [
        bin_name,
        "-t",
        "-p",
        prompt,
        "-m",
        model,
        "--max-turns",
        str(max_turns),
        "--output-format",
        output_format,
        "--skip-onboarding",
        "--no-session",
    ]
    return argv


def parse_cmd_stdout(stdout: str, *, fallback_text: bool = True) -> str:
    """Parse Command Code `--output-format json` NDJSON, or plain text.

    Walk line by line (the event stream can be long). The last object with
    `type == "result"` wins. `sessionId` / `stopReason` are optional and must
    not be required — early auth failures omit them.
    """
    last_result: dict[str, Any] | None = None
    non_json_lines: list[str] = []
    for raw in stdout.splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            non_json_lines.append(raw)
            continue
        if not isinstance(obj, dict):
            continue
        if obj.get("type") == "result":
            last_result = obj
    if last_result is None:
        if fallback_text:
            text = "\n".join(non_json_lines).strip() or stdout.strip()
            if text:
                return text
        raise LLMError("Command Code produced no result line")

    subtype = last_result.get("subtype") or "success"
    if subtype == "error":
        err = last_result.get("error") or "Command Code error result"
        raise LLMError(str(err))
    text = last_result.get("finalText")
    if text is None:
        text = last_result.get("result") or last_result.get("text") or ""
    text = str(text)
    if subtype == "max_turns" and not text.strip():
        raise LLMError("max turns reached before a final answer")
    return text


def _strip_fences(text: str) -> str:
    stripped = text.strip()
    # Handle one or more markdown fences; keep the first fenced body if present.
    fence = re.search(r"```(?:json|JSON)?\s*\n?(.*?)```", stripped, flags=re.DOTALL)
    if fence:
        return fence.group(1).strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[-1]
        if stripped.endswith("```"):
            stripped = stripped[: stripped.rfind("```")]
        stripped = stripped.strip()
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    return stripped


def _normalize_quotes(text: str) -> str:
    return text.translate(_SMART_QUOTES)


def _strip_trailing_commas(text: str) -> str:
    # Remove trailing commas before } or ] (common LLM junk).
    return re.sub(r",(\s*[}\]])", r"\1", text)


def _extract_balanced_object(text: str) -> str | None:
    """Return the first balanced {...} slice, respecting string literals."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _candidate_slices(text: str) -> list[str]:
    """Generate candidate JSON object strings from model text."""
    candidates: list[str] = []
    stripped = _strip_fences(text)
    candidates.append(stripped)

    balanced = _extract_balanced_object(stripped)
    if balanced:
        candidates.append(balanced)

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(stripped[start : end + 1])

    # Deduplicate while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _try_loads(candidate: str) -> dict[str, Any] | None:
    variants = [
        candidate,
        _strip_trailing_commas(candidate),
        _normalize_quotes(candidate),
        _strip_trailing_commas(_normalize_quotes(candidate)),
    ]
    seen: set[str] = set()
    for v in variants:
        if v in seen:
            continue
        seen.add(v)
        try:
            obj = json.loads(v)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def parse_json_object(text: str) -> dict[str, Any]:
    """Pull a JSON object out of model text (fences, trailing commas, smart quotes)."""
    if not text or not str(text).strip():
        raise LLMError("model output is not a JSON object")

    last_err: Exception | None = None
    for candidate in _candidate_slices(text):
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError as exc:
            last_err = exc
        cleaned = _try_loads(candidate)
        if cleaned is not None:
            return cleaned

    if last_err is not None:
        raise LLMError(f"model JSON parse failed: {last_err}") from last_err
    raise LLMError("model output is not a JSON object")


class CommandCodeRunner(LLMRunner):
    name = "cmd"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        bin_name: str = CMD_BIN,
        env: dict[str, str] | None = None,
        timeout_sec: int = 180,
        cwd: str | None = None,
    ) -> None:
        self.model = model
        self.bin_name = bin_name
        self.env = env
        self.timeout_sec = timeout_sec
        self.cwd = cwd

    def complete(self, prompt: str, *, max_turns: int = 4, label: str = "") -> str:
        binary = shutil.which(self.bin_name) or self.bin_name
        if shutil.which(self.bin_name) is None and not os.path.isfile(self.bin_name):
            raise LLMError(
                f"`{self.bin_name}` not found. Install with `npm i -g command-code` "
                "(Node >= 22), or use --runner mock."
            )
        merged = os.environ.copy()
        if self.env:
            merged.update(self.env)
        if not merged.get("COMMAND_CODE_API_KEY"):
            raise LLMError(
                "COMMAND_CODE_API_KEY is not set. The CLI reads this env var at "
                "startup (it overrides ~/.commandcode/auth.json)."
            )
        argv = build_cmd_argv(prompt, self.model, max_turns, bin_name=binary)
        log.info("cmd %s model=%s turns=%d chars=%d", label or "complete", self.model, max_turns, len(prompt))
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                env=merged,
                timeout=self.timeout_sec,
                cwd=self.cwd,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise LLMError(f"Command Code timed out after {self.timeout_sec}s") from exc

        if proc.returncode not in (0, EXIT_MAX_TURNS) and not proc.stdout.strip():
            stderr = (proc.stderr or "").strip()[:800]
            hint = {
                EXIT_AUTH: "not authenticated (check COMMAND_CODE_API_KEY)",
                EXIT_CREDITS: "insufficient credits",
                EXIT_NO_RESPONSE: "model produced no response",
            }.get(proc.returncode, f"exit {proc.returncode}")
            raise LLMError(f"Command Code failed: {hint}. {stderr}".strip())

        try:
            return parse_cmd_stdout(proc.stdout)
        except LLMError:
            if proc.returncode == EXIT_MAX_TURNS:
                # Partial stdout is still the documented behavior.
                partial = parse_cmd_stdout(proc.stdout, fallback_text=True)
                if partial:
                    return partial
            raise
