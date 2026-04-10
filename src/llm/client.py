"""
Claude CLI 客户端封装

通过 subprocess 调用本地 Claude Code CLI (node cli.js -p)，
绕过直接 API 调用限制（适用于 packyapi 等仅允许 CLI 访问的代理）。
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

# 默认路径（可被 .env 覆盖）
_DEFAULT_NODE = "node"
_DEFAULT_CLI_JS = str(
    Path(os.environ.get("APPDATA", "")) / "../Roaming/npm/node_modules/@anthropic-ai/claude-code/cli.js"
)


def _get_env() -> dict:
    """构建调用 CLI 所需的环境变量"""
    env = os.environ.copy()
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
    git_bash = os.environ.get("CLAUDE_CODE_GIT_BASH_PATH", "")
    if api_key:
        env["ANTHROPIC_API_KEY"] = api_key
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url
    if git_bash:
        env["CLAUDE_CODE_GIT_BASH_PATH"] = git_bash
    return env


def _build_cli_args(system_prompt: str, user_content: str) -> list[str]:
    node_exe = os.environ.get("NODE_PATH", _DEFAULT_NODE)
    cli_js = os.environ.get("CLAUDE_CLI_JS", _DEFAULT_CLI_JS)
    return [
        node_exe,
        cli_js,
        "-p",
        "--bare",
        "--output-format",
        "text",
        "--system-prompt",
        system_prompt,
        user_content,
    ]


def _call_claude_sync(
    system_prompt: str,
    user_content: str,
    timeout: int = 180,
    max_retries: int = 3,
) -> str:
    """
    通过 Claude CLI 同步调用 Claude 模型，返回文本响应。
    """
    env = _get_env()
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                _build_cli_args(system_prompt, user_content),
                capture_output=True,
                env=env,
                timeout=timeout,
            )
            # Decode bytes manually: try UTF-8 first, fall back to system encoding
            raw_bytes = result.stdout
            try:
                stdout = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                stdout = raw_bytes.decode("gbk", errors="replace")

            raw_err = result.stderr
            try:
                stderr = raw_err.decode("utf-8")
            except UnicodeDecodeError:
                stderr = raw_err.decode("gbk", errors="replace")

            if result.returncode == 0 and stdout.strip():
                return stdout.strip()

            err = stderr.strip() or f"exit code {result.returncode}"
            raise RuntimeError(f"CLI error: {err[:200]}")

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

    raise RuntimeError(f"Claude CLI failed after {max_retries} attempts: {last_error}")


def _extract_json(text: str) -> str:
    """从 LLM 响应中提取 JSON 对象 — 处理 claude -p 可能附加的额外文本"""
    text = text.strip()

    # Strip markdown code block wrappers
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # If already valid JSON, return directly
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Find the first { ... } block with proper brace matching
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
    """Claude CLI 客户端封装 — 通过 node cli.js -p 调用，支持异步并发控制"""

    def __init__(self, max_concurrency: int = 3):
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._total_calls = 0
        self._total_tokens = 0

    async def call(
        self,
        system_prompt: str,
        user_content: str,
        max_retries: int = 3,
        max_tokens: int = 4096,
    ) -> str:
        """异步调用 Claude CLI（内部通过 run_in_executor 包装同步 subprocess）"""
        async with self._semaphore:
            start = time.time()

            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                lambda: _call_claude_sync(
                    system_prompt=system_prompt,
                    user_content=user_content,
                    timeout=180,
                    max_retries=max_retries,
                ),
            )

            elapsed = time.time() - start
            self._total_calls += 1
            logger.debug(
                f"LLM call #{self._total_calls} | "
                f"{elapsed:.1f}s | "
                f"output: {len(text)} chars"
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
        """调用 Claude 并用 Pydantic 校验返回结果，失败时注入错误信息重试"""
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
                # Extract JSON from response (handles extra text from CLI)
                text = _extract_json(text)

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
                logger.error(f"LLM call failed during validation attempt {attempt}: {e}")
                last_error = str(e)

        raise RuntimeError(
            f"Validation failed after {max_retries} attempts for {response_model.__name__}: {last_error}"
        )

    @property
    def stats(self) -> dict:
        return {
            "total_calls": self._total_calls,
            "total_tokens": self._total_tokens,
        }
