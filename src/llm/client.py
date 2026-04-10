import asyncio
import time

import anthropic
from loguru import logger
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
import os

load_dotenv()


class ClaudeClient:
    """Claude API 异步客户端封装 — 统一处理重试、校验、日志"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "claude-sonnet-4-20250514",
        max_concurrency: int = 5,
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.base_url = base_url or os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        self.model = model
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._client = anthropic.AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        self._total_calls = 0
        self._total_tokens = 0

    async def call(
        self,
        system_prompt: str,
        user_content: str,
        max_retries: int = 3,
        max_tokens: int = 4096,
    ) -> str:
        """调用 Claude API 并返回原始文本响应"""
        async with self._semaphore:
            last_error = None
            for attempt in range(1, max_retries + 1):
                try:
                    start = time.time()
                    response = await self._client.messages.create(
                        model=self.model,
                        max_tokens=max_tokens,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_content}],
                    )
                    elapsed = time.time() - start
                    text = response.content[0].text

                    self._total_calls += 1
                    input_tokens = getattr(response.usage, "input_tokens", 0)
                    output_tokens = getattr(response.usage, "output_tokens", 0)
                    self._total_tokens += input_tokens + output_tokens

                    logger.debug(
                        f"LLM call #{self._total_calls} | "
                        f"{elapsed:.1f}s | "
                        f"tokens: {input_tokens}+{output_tokens}"
                    )
                    return text

                except anthropic.RateLimitError:
                    wait = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait}s (attempt {attempt})")
                    await asyncio.sleep(wait)
                    last_error = "RateLimitError"

                except anthropic.APITimeoutError:
                    wait = 2 ** attempt
                    logger.warning(f"API timeout, waiting {wait}s (attempt {attempt})")
                    await asyncio.sleep(wait)
                    last_error = "APITimeoutError"

                except Exception as e:
                    logger.error(f"LLM call error (attempt {attempt}): {e}")
                    last_error = str(e)
                    if attempt < max_retries:
                        await asyncio.sleep(1)

            raise RuntimeError(f"LLM call failed after {max_retries} attempts: {last_error}")

    async def call_with_validation(
        self,
        system_prompt: str,
        user_content: str,
        response_model: type[BaseModel],
        max_retries: int = 3,
        max_tokens: int = 4096,
    ) -> BaseModel:
        """调用 Claude API 并用 Pydantic 校验返回结果，失败时注入错误信息重试"""
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
                # Strip potential markdown code block wrappers
                text = text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

                result = response_model.model_validate_json(text)
                return result

            except ValidationError as e:
                last_error = str(e)
                logger.warning(
                    f"Validation failed (attempt {attempt}/{max_retries}): {last_error[:200]}"
                )
                # Inject error info for next retry
                current_content = (
                    f"{user_content}\n\n"
                    f"# IMPORTANT: Your previous output had validation errors:\n"
                    f"{last_error}\n"
                    f"Please fix these issues and output valid JSON."
                )

            except RuntimeError as e:
                logger.error(f"LLM call failed during validation attempt {attempt}: {e}")
                last_error = str(e)

        raise ValidationError.from_exception_data(
            title=response_model.__name__,
            line_errors=[],
        ) if False else RuntimeError(
            f"Validation failed after {max_retries} attempts for {response_model.__name__}: {last_error}"
        )

    @property
    def stats(self) -> dict:
        return {
            "total_calls": self._total_calls,
            "total_tokens": self._total_tokens,
        }
