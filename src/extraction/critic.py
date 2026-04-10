import asyncio
import json
from loguru import logger
from src.models import StructuredArticle, ScoredArticle, EvaluationMatrix, ScoreItem, ImpactScoreItem, TargetDomain
from src.llm.client import ClaudeClient
from src.llm.prompts import PromptManager

SYSTEM_PROMPT = "你是 AI 领域资深架构师与技术评委 (Critic Agent)。请严格按照指示输出合法 JSON。"

def _default_evaluation() -> EvaluationMatrix:
    """Return a default evaluation matrix with all scores set to 3"""
    return EvaluationMatrix(
        technical_novelty=ScoreItem(score=3, justification="默认评分"),
        potential_impact=ImpactScoreItem(score=3, target_domain=TargetDomain.GENERAL_AI, justification="默认评分"),
        readiness_level=ScoreItem(score=3, justification="默认评分"),
        trend_insight=None,
        critical_risks=[],
    )

async def score_one(
    article: StructuredArticle,
    client: ClaudeClient,
    prompt_mgr: PromptManager,
) -> ScoredArticle:
    """Score a single article using the Critic Agent"""
    # Serialize the structured article for the prompt (only the LLM-extracted fields)
    article_data = {
        "title": article.title,
        "category": article.category.value,
        "core_entities": article.core_entities,
        "structured_analysis": article.structured_analysis.model_dump(),
        "trend_insight": article.trend_insight,
        "risk_or_opportunity": article.risk_or_opportunity,
    }

    try:
        user_content = prompt_mgr.render(
            "critic",
            structured_article_json=json.dumps(article_data, ensure_ascii=False, indent=2),
            original_title=article.original_title,
            source_name=article.source_name,
        )
        evaluation = await client.call_with_validation(
            system_prompt=SYSTEM_PROMPT,
            user_content=user_content,
            response_model=EvaluationMatrix,
            max_retries=3,
        )
    except Exception as e:
        logger.warning(f"Scoring failed for '{article.title[:30]}...': {e}, using defaults")
        evaluation = _default_evaluation()

    # Create ScoredArticle from StructuredArticle + evaluation
    scored_data = article.model_dump()
    scored_data["evaluation"] = evaluation
    scored_data["impact_score"] = 0  # computed later in compute layer
    scored_data["final_score"] = 0.0  # computed later in compute layer
    scored_data["source_weight"] = 1.0  # will be set from config
    return ScoredArticle.model_validate(scored_data)

async def score_batch(
    articles: list[StructuredArticle],
    client: ClaudeClient,
    prompt_mgr: PromptManager,
) -> list[ScoredArticle]:
    """Score all articles in parallel"""
    tasks = [score_one(a, client, prompt_mgr) for a in articles]
    results = await asyncio.gather(*tasks)
    logger.info(f"Scoring: {len(results)}/{len(articles)} completed")
    return results
