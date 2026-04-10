import asyncio
import json
from loguru import logger
from src.models import RawArticle, StructuredArticle
from src.llm.client import ClaudeClient
from src.llm.prompts import PromptManager

SYSTEM_PROMPT = "你是一个 AI 行业信息结构化抽取引擎。请严格按照指示输出合法 JSON。"

async def extract_one(
    article: RawArticle,
    client: ClaudeClient,
    prompt_mgr: PromptManager,
) -> StructuredArticle | None:
    """Extract structured data from a single article"""
    try:
        user_content = prompt_mgr.render(
            "extraction",
            title=article.title,
            source_name=article.source_name,
            published_at=str(article.published_at),
            language=article.language,
            content=article.content,
        )
        result = await client.call_with_validation(
            system_prompt=SYSTEM_PROMPT,
            user_content=user_content,
            response_model=StructuredArticle,
            max_retries=3,
        )
        # Set preserved fields from the original article
        result.original_title = article.title
        result.original_url = article.url
        result.source_name = article.source_name
        result.published_at = article.published_at
        result.language = article.language
        return result
    except Exception as e:
        logger.error(f"Extraction failed for '{article.title[:30]}...': {e}")
        return None

async def extract_batch(
    articles: list[RawArticle],
    client: ClaudeClient,
    prompt_mgr: PromptManager,
) -> list[StructuredArticle]:
    """Extract structured data from all articles in parallel"""
    tasks = [extract_one(a, client, prompt_mgr) for a in articles]
    results = await asyncio.gather(*tasks)
    valid = [r for r in results if r is not None]
    logger.info(f"Extraction: {len(valid)}/{len(articles)} succeeded")
    return valid
