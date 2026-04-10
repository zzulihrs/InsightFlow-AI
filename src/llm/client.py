"""
Claude CLI 客户端封装

通过 subprocess 调用本地 Claude Code CLI (node cli.js -p)。
用户 prompt 经由 stdin 传入，避免 Windows 命令行长度限制导致长 prompt 超时/挂起。
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_NODE   = "node"
_DEFAULT_CLI_JS = str(
    Path(os.environ.get("APPDATA", ""))
    / "../Roaming/npm/node_modules/@anthropic-ai/claude-code/cli.js"
)


def _get_env() -> dict:
    env = os.environ.copy()
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL", "CLAUDE_CODE_GIT_BASH_PATH"):
        val = os.environ.get(key, "")
        if val:
            env[key] = val
    return env


def _build_cli_args(system_prompt: str) -> list[str]:
    """Build CLI args WITHOUT user_content — prompt is passed via stdin."""
    node_exe = os.environ.get("NODE_PATH", _DEFAULT_NODE)
    cli_js   = os.environ.get("CLAUDE_CLI_JS", _DEFAULT_CLI_JS)
    return [
        node_exe,
        cli_js,
        "-p",
        "--bare",
        "--output-format", "text",
        "--system-prompt", system_prompt,
        # user_content is NOT here — sent via stdin
    ]


def _call_claude_sync(
    system_prompt: str,
    user_content: str,
    timeout: int = 120,
    max_retries: int = 3,
) -> str:
    """
    通过 Claude CLI 同步调用，user_content 经 stdin 传入。
    避免 Windows 命令行长度上限（约 8,191 字符）导致长 prompt 挂起。
    """
    env       = _get_env()
    args      = _build_cli_args(system_prompt)
    stdin_raw = user_content.encode("utf-8")
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                args,
                input=stdin_raw,          # ← prompt via stdin
                capture_output=True,
                env=env,
                timeout=timeout,
            )
            try:
                stdout = result.stdout.decode("utf-8")
            except UnicodeDecodeError:
                stdout = result.stdout.decode("gbk", errors="replace")

            try:
                stderr = result.stderr.decode("utf-8")
            except UnicodeDecodeError:
                stderr = result.stderr.decode("gbk", errors="replace")

            if result.returncode == 0 and stdout.strip():
                logger.debug(
                    f"CLI call OK (attempt {attempt}) | {len(stdout)} chars returned"
                )
                return stdout.strip()

            err = stderr.strip() or f"exit code {result.returncode}"
            raise RuntimeError(f"CLI error: {err[:300]}")

        except subprocess.TimeoutExpired:
            last_error = RuntimeError(f"Claude CLI timeout ({timeout}s)")
            logger.warning(f"CLI timeout (attempt {attempt}/{max_retries})")
            if attempt < max_retries:
                time.sleep(2)
        except RuntimeError:
            raise
        except Exception as e:
            last_error = e
            logger.error(f"CLI call error (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(2)

    raise RuntimeError(
        f"Claude CLI failed after {max_retries} attempts: {last_error}"
    )


def _extract_json(text: str) -> str:
    """从 LLM 响应中提取 JSON 对象或数组。"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Try finding a JSON array first
    arr_start = text.find("[")
    obj_start = text.find("{")
    if arr_start != -1 and (obj_start == -1 or arr_start < obj_start):
        # Extract [...] array
        depth = 0
        in_string = False
        escape_next = False
        for i in range(arr_start, len(text)):
            ch = text[i]
            if escape_next:
                escape_next = False
                continue
            if ch == "\\":
                escape_next = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    candidate = text[arr_start:i + 1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except json.JSONDecodeError:
                        break
        # Fall through to object extraction

    start = text.find("{")
    if start == -1:
        return text

    depth = 0
    in_string = False
    escape_next = False
    end = start

    for i in range(start, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    extracted = text[start:end + 1]
    try:
        json.loads(extracted)
        return extracted
    except json.JSONDecodeError:
        return text


class ClaudeClient:
    """Claude CLI 客户端封装 — 通过 node cli.js -p（stdin 模式）调用"""

    def __init__(self, max_concurrency: int = 3):
        self._semaphore   = asyncio.Semaphore(max_concurrency)
        self._total_calls = 0
        self._total_tokens = 0

    async def call(
        self,
        system_prompt: str,
        user_content: str,
        max_retries: int = 3,
        max_tokens: int = 4096,
    ) -> str:
        async with self._semaphore:
            start = time.time()
            loop  = asyncio.get_event_loop()
            text  = await loop.run_in_executor(
                None,
                lambda: _call_claude_sync(
                    system_prompt=system_prompt,
                    user_content=user_content,
                    timeout=150,
                    max_retries=max_retries,
                ),
            )
            self._total_calls += 1
            logger.debug(
                f"LLM call #{self._total_calls} | {time.time()-start:.1f}s | {len(text)} chars"
            )
            return text

    async def call_with_validation(
        self,
        system_prompt: str,
        user_content: str,
        response_model: type[BaseModel],
        max_retries: int = 3,
        max_tokens: int = 4096,
    ) -> BaseModel:
        current_content = user_content
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                text = await self.call(
                    system_prompt=system_prompt,
                    user_content=current_content,
                    max_retries=2,
                    max_tokens=max_tokens,
                )
                text   = _extract_json(text)
                result = response_model.model_validate_json(text)
                return result

            except ValidationError as e:
                last_error = str(e)
                logger.warning(
                    f"Validation failed (attempt {attempt}/{max_retries}): {last_error[:200]}"
                )
                current_content = (
                    f"{user_content}\n\n"
                    f"# IMPORTANT: Your previous output had validation errors:\n"
                    f"{last_error}\n"
                    f"Please fix and output ONLY valid JSON, no other text."
                )
            except RuntimeError as e:
                logger.error(f"LLM call failed (attempt {attempt}): {e}")
                last_error = str(e)

        raise RuntimeError(
            f"Validation failed after {max_retries} attempts for "
            f"{response_model.__name__}: {last_error}"
        )

    @property
    def stats(self) -> dict:
        return {
            "total_calls": self._total_calls,
            "total_tokens": self._total_tokens,
        }
