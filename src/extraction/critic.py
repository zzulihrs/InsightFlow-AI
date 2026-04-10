from loguru import logger

from src.models import (
    EvaluationMatrix,
    ImpactScoreItem,
    ScoreItem,
    ScoredArticle,
    StructuredArticle,
    TargetDomain,
)
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


def _heuristic_evaluation(article: StructuredArticle) -> EvaluationMatrix:
    text = (
        f"{article.title} "
        f"{article.original_title} "
        f"{article.structured_analysis.key_action} "
        f"{article.structured_analysis.technical_implication}"
    ).lower()

    novelty = 3
    if any(kw in text for kw in ["oral", "论文", "iclr", "native", "原地", "多模态", "agent", "reasoning"]):
        novelty = 5
    elif any(kw in text for kw in ["preview", "introducing", "launch", "发布", "推出", "open source"]):
        novelty = 4

    impact = 3
    if any(
        kw in text for kw in [
            "openai", "anthropic", "meta", "microsoft", "阿里", "字节", "gpt-5.4", "claude", "mcp",
            "融资", "funding", "raises", "bill", "法案",
        ]
    ):
        impact = 5
    elif any(kw in text for kw in ["github", "arxiv", "趋势", "预测", "ecosystem", "平台"]):
        impact = 4

    readiness = 3
    if article.category.value in {"产品发布", "商业资本"}:
        readiness = 4
    if any(kw in text for kw in ["launch", "上线", "推出", "release", "preview", "已被", "ranking", "榜单"]):
        readiness = 5
    elif any(kw in text for kw in ["论文", "预测", "discussion", "预测", "research"]):
        readiness = 3

    target_domain = TargetDomain.GENERAL_AI
    if any(kw in text for kw in ["agent", "mcp", "workflow", "工具调用"]):
        target_domain = TargetDomain.SOFTWARE_ENGINEERING
    elif any(kw in text for kw in ["api", "模型", "model", "inference", "reasoning"]):
        target_domain = TargetDomain.ML_SYSTEMS
    elif any(kw in text for kw in ["open source", "github", "repo"]):
        target_domain = TargetDomain.SOFTWARE_ENGINEERING

    risks: list[str] = []
    if article.structured_analysis.sentiment_polarity.value == "Negative":
        risks.append("需评估迁移成本、稳定性或监管约束。")
    if article.category.value == "政策合规":
        risks.append("政策变化可能改变产品发布和数据使用边界。")

    return EvaluationMatrix(
        technical_novelty=ScoreItem(
            score=novelty,
            justification="基于标题与关键信息中的技术突破、研究新意和能力边界变化进行启发式评分。",
        ),
        potential_impact=ImpactScoreItem(
            score=impact,
            target_domain=target_domain,
            justification="结合主体影响力、事件类型和可能波及的开发生态范围进行启发式评分。",
        ),
        readiness_level=ScoreItem(
            score=readiness,
            justification="根据是否已发布、是否可用以及离产品化距离进行启发式评分。",
        ),
        trend_insight=article.trend_insight,
        critical_risks=risks,
    )


async def score_batch(
    articles: list[StructuredArticle],
    client: ClaudeClient,
    prompt_mgr: PromptManager,
) -> list[ScoredArticle]:
    """Score all articles using heuristics (no LLM calls)."""
    results = []
    for article in articles:
        evaluation = _heuristic_evaluation(article)
        scored_data = article.model_dump()
        scored_data["evaluation"] = evaluation
        scored_data["impact_score"] = 0   # computed later in compute layer
        scored_data["final_score"] = 0.0  # computed later in compute layer
        scored_data["source_weight"] = 1.0
        results.append(ScoredArticle.model_validate(scored_data))
    logger.info(f"Scoring (heuristic): {len(results)}/{len(articles)} completed")
    return results
