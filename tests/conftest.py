"""Shared pytest fixtures for all test modules."""

from datetime import datetime

import pytest

from src.models.article import (
    ArticleCategory,
    RawArticle,
    SentimentPolarity,
    StructuredAnalysis,
    StructuredArticle,
    ScoredArticle,
)
from src.models.evaluation import (
    EvaluationMatrix,
    ImpactScoreItem,
    ScoreItem,
    TargetDomain,
)
from src.models.report import (
    DataFilterRules,
    DailyReport,
    FilteredContext,
    HotEvent,
    TrendInsight,
    RiskOpportunity,
)
from src.models.source import SourceType


# ── Primitive builders ────────────────────────────────────────────────────────

def make_raw_article(
    *,
    title: str = "OpenAI 发布 GPT-5",
    content: str = "OpenAI 宣布发布 GPT-5，参数量超过一万亿。",
    source_name: str = "OpenAI Blog",
    source_type: SourceType = SourceType.STATIC,
    url: str = "https://openai.com/gpt-5",
    published_at: datetime | None = None,
    language: str = "zh",
    source_weight: float = 1.5,
) -> RawArticle:
    return RawArticle(
        source_name=source_name,
        source_type=source_type,
        title=title,
        content=content,
        url=url,
        published_at=published_at or datetime(2026, 4, 10, 12, 0),
        language=language,
        source_weight=source_weight,
    )


def make_structured_analysis(
    *,
    background: str = "GPT 是 OpenAI 开发的大语言模型系列",
    key_action: str = "OpenAI 正式发布 GPT-5",
    technical_implication: str = "推理能力大幅提升，或取代现有代码生成工具",
    sentiment: SentimentPolarity = SentimentPolarity.POSITIVE,
) -> StructuredAnalysis:
    return StructuredAnalysis(
        background=background,
        key_action=key_action,
        technical_implication=technical_implication,
        sentiment_polarity=sentiment,
    )


def make_structured_article(
    *,
    title: str = "GPT-5 正式发布",
    category: ArticleCategory = ArticleCategory.PRODUCT_RELEASE,
    core_entities: list[str] | None = None,
    source_name: str = "OpenAI Blog",
    original_url: str = "https://openai.com/gpt-5",
    published_at: datetime | None = None,
    language: str = "en",
) -> StructuredArticle:
    return StructuredArticle(
        title=title,
        category=category,
        core_entities=core_entities or ["OpenAI", "GPT-5"],
        structured_analysis=make_structured_analysis(),
        trend_insight="大模型参数规模持续扩张",
        risk_or_opportunity="开发者需尽快评估 API 成本",
        original_title="Introducing GPT-5",
        original_url=original_url,
        source_name=source_name,
        published_at=published_at or datetime(2026, 4, 10, 12, 0),
        language=language,
    )


def make_evaluation_matrix(
    *,
    novelty: int = 4,
    impact: int = 5,
    readiness: int = 4,
    domain: TargetDomain = TargetDomain.GENERAL_AI,
) -> EvaluationMatrix:
    return EvaluationMatrix(
        technical_novelty=ScoreItem(score=novelty, justification="有显著创新"),
        potential_impact=ImpactScoreItem(
            score=impact,
            justification="行业级影响",
            target_domain=domain,
        ),
        readiness_level=ScoreItem(score=readiness, justification="已可商用"),
    )


def make_scored_article(
    *,
    title: str = "GPT-5 正式发布",
    category: ArticleCategory = ArticleCategory.PRODUCT_RELEASE,
    core_entities: list[str] | None = None,
    source_name: str = "OpenAI Blog",
    original_url: str = "https://openai.com/gpt-5",
    novelty: int = 4,
    impact: int = 5,
    readiness: int = 4,
    impact_score: int = 0,
    final_score: float = 0.0,
    source_weight: float = 1.5,
) -> ScoredArticle:
    return ScoredArticle(
        title=title,
        category=category,
        core_entities=core_entities or ["OpenAI", "GPT-5"],
        structured_analysis=make_structured_analysis(),
        trend_insight="大模型参数规模持续扩张",
        risk_or_opportunity="开发者需尽快评估 API 成本",
        original_title="Introducing GPT-5",
        original_url=original_url,
        source_name=source_name,
        published_at=datetime(2026, 4, 10, 12, 0),
        language="en",
        evaluation=make_evaluation_matrix(
            novelty=novelty,
            impact=impact,
            readiness=readiness,
        ),
        impact_score=impact_score,
        final_score=final_score,
        source_weight=source_weight,
    )


def make_hot_event(
    *,
    rank: int = 1,
    title: str = "GPT-5 正式发布",
    impact_score: int = 9,
    category: ArticleCategory = ArticleCategory.PRODUCT_RELEASE,
    summary: str = "OpenAI 发布 GPT-5，参数超过万亿，推理能力大幅提升。该模型将改变 AI 应用格局。",
    source_url: str = "https://openai.com/gpt-5",
    background: str = "GPT-5 是 OpenAI 的第五代大语言模型；参数量指模型内部权重数量。",
    tags: list[str] | None = None,
    reference_links: list[str] | None = None,
) -> HotEvent:
    return HotEvent(
        rank=rank,
        title=title,
        impact_score=impact_score,
        category=category,
        summary=summary,
        source_url=source_url,
        background=background,
        tags=tags if tags is not None else ["#AI", "#GPT", "#OpenAI"],
        reference_links=reference_links if reference_links is not None else [
            "OpenAI 官方博客 — Introducing GPT-5",
            "GPT-5 技术报告 (arXiv)",
        ],
    )


def make_daily_report(
    *,
    report_date: str = "2026-04-10",
    hot_events: list[HotEvent] | None = None,
    executive_summary_zh: str = "今日 AI 领域重大发布：GPT-5 正式推出。",
    executive_summary_en: str = "GPT-5 was officially released today by OpenAI.",
    total_articles_processed: int = 20,
    total_articles_after_filter: int = 15,
) -> DailyReport:
    events = hot_events if hot_events is not None else [make_hot_event()]
    return DailyReport(
        report_date=report_date,
        generated_at=datetime(2026, 4, 10, 14, 0),
        total_articles_processed=total_articles_processed,
        total_articles_after_filter=total_articles_after_filter,
        hot_events=events,
        executive_summary_zh=executive_summary_zh,
        executive_summary_en=executive_summary_en,
    )


def make_data_filter_rules(
    *,
    top_k: int = 3,
    min_impact_score: int = 7,
    exclude_categories: list[str] | None = None,
) -> DataFilterRules:
    return DataFilterRules(
        top_k=top_k,
        min_impact_score=min_impact_score,
        exclude_categories=exclude_categories or [],
    )


# ── Pytest fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def raw_article():
    return make_raw_article()


@pytest.fixture
def structured_article():
    return make_structured_article()


@pytest.fixture
def scored_article():
    return make_scored_article()


@pytest.fixture
def hot_event():
    return make_hot_event()


@pytest.fixture
def daily_report():
    return make_daily_report()


@pytest.fixture
def filter_rules():
    return make_data_filter_rules()
