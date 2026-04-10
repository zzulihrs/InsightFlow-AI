"""Unit tests for Pydantic data models, including the updated HotEvent."""

import pytest
from pydantic import ValidationError

from src.models.article import ArticleCategory, SentimentPolarity, StructuredAnalysis
from src.models.evaluation import EvaluationMatrix, ImpactScoreItem, ScoreItem, TargetDomain
from src.models.report import (
    DataFilterRules,
    DailyReport,
    DeepDive,
    HotEvent,
    RiskOpportunity,
    TrendInsight,
)
from tests.conftest import (
    make_evaluation_matrix,
    make_hot_event,
    make_daily_report,
    make_scored_article,
)


# ── HotEvent model ────────────────────────────────────────────────────────────

class TestHotEvent:
    def test_all_new_fields_have_defaults(self):
        """background, tags, reference_links must all default gracefully."""
        ev = HotEvent(
            rank=1,
            title="测试事件",
            impact_score=8,
            category=ArticleCategory.TECH_BREAKTHROUGH,
            summary="这是一条测试摘要。",
            source_url="https://example.com",
        )
        assert ev.background == ""
        assert ev.tags == []
        assert ev.reference_links == []

    def test_create_with_all_fields(self):
        ev = make_hot_event(
            background="GPT-5 是 OpenAI 的最新模型。",
            tags=["#AI", "#LLM"],
            reference_links=["OpenAI 博客"],
        )
        assert ev.background == "GPT-5 是 OpenAI 的最新模型。"
        assert ev.tags == ["#AI", "#LLM"]
        assert ev.reference_links == ["OpenAI 博客"]

    def test_rank_stored_correctly(self):
        ev = make_hot_event(rank=3)
        assert ev.rank == 3

    def test_impact_score_within_range(self):
        ev = make_hot_event(impact_score=10)
        assert ev.impact_score == 10

    def test_category_is_enum(self):
        ev = make_hot_event(category=ArticleCategory.BUSINESS_CAPITAL)
        assert ev.category == ArticleCategory.BUSINESS_CAPITAL

    def test_tags_can_be_empty_list(self):
        ev = make_hot_event(tags=[])
        assert ev.tags == []

    def test_reference_links_can_be_empty_list(self):
        ev = make_hot_event(reference_links=[])
        assert ev.reference_links == []

    def test_multiple_tags(self):
        tags = ["#AI", "#OpenAI", "#GPT", "#LLM", "#Technology"]
        ev = make_hot_event(tags=tags)
        assert ev.tags == tags

    def test_model_dump_includes_new_fields(self):
        ev = make_hot_event(
            background="背景信息",
            tags=["#AI"],
            reference_links=["参考资源1"],
        )
        dumped = ev.model_dump()
        assert "background" in dumped
        assert "tags" in dumped
        assert "reference_links" in dumped
        assert dumped["background"] == "背景信息"
        assert dumped["tags"] == ["#AI"]
        assert dumped["reference_links"] == ["参考资源1"]

    def test_json_serialization_includes_new_fields(self):
        ev = make_hot_event(background="技术背景")
        data = ev.model_dump(mode="json")
        assert data["background"] == "技术背景"


# ── ArticleCategory ───────────────────────────────────────────────────────────

class TestArticleCategory:
    def test_all_four_categories_exist(self):
        assert ArticleCategory.TECH_BREAKTHROUGH.value == "技术突破"
        assert ArticleCategory.BUSINESS_CAPITAL.value == "商业资本"
        assert ArticleCategory.PRODUCT_RELEASE.value == "产品发布"
        assert ArticleCategory.POLICY_COMPLIANCE.value == "政策合规"

    def test_category_from_string(self):
        cat = ArticleCategory("技术突破")
        assert cat == ArticleCategory.TECH_BREAKTHROUGH


# ── SentimentPolarity ─────────────────────────────────────────────────────────

class TestSentimentPolarity:
    def test_three_values_exist(self):
        assert SentimentPolarity.POSITIVE.value == "Positive"
        assert SentimentPolarity.NEUTRAL.value == "Neutral"
        assert SentimentPolarity.NEGATIVE.value == "Negative"


# ── EvaluationMatrix ──────────────────────────────────────────────────────────

class TestEvaluationMatrix:
    def test_scores_must_be_1_to_5(self):
        with pytest.raises(ValidationError):
            ScoreItem(score=0, justification="太低了")
        with pytest.raises(ValidationError):
            ScoreItem(score=6, justification="太高了")

    def test_valid_score_item(self):
        item = ScoreItem(score=3, justification="中等")
        assert item.score == 3

    def test_impact_score_item_has_target_domain(self):
        item = ImpactScoreItem(
            score=4,
            justification="行业影响大",
            target_domain=TargetDomain.GENERAL_AI,
        )
        assert item.target_domain == TargetDomain.GENERAL_AI

    def test_evaluation_matrix_created(self):
        ev = make_evaluation_matrix(novelty=3, impact=4, readiness=5)
        assert ev.technical_novelty.score == 3
        assert ev.potential_impact.score == 4
        assert ev.readiness_level.score == 5

    def test_critical_risks_defaults_empty(self):
        ev = make_evaluation_matrix()
        assert ev.critical_risks == []

    def test_trend_insight_defaults_none(self):
        ev = make_evaluation_matrix()
        assert ev.trend_insight is None


# ── ScoredArticle ─────────────────────────────────────────────────────────────

class TestScoredArticle:
    def test_default_impact_and_final_score_are_zero(self):
        sa = make_scored_article(impact_score=0, final_score=0.0)
        assert sa.impact_score == 0
        assert sa.final_score == 0.0

    def test_source_weight_stored(self):
        sa = make_scored_article(source_weight=1.3)
        assert sa.source_weight == 1.3

    def test_impact_score_range(self):
        # 10 is valid
        sa = make_scored_article(impact_score=10)
        assert sa.impact_score == 10

    def test_evaluation_attached(self):
        sa = make_scored_article(novelty=5, impact=5, readiness=5)
        assert sa.evaluation.technical_novelty.score == 5

    def test_core_entities_present(self):
        sa = make_scored_article(core_entities=["OpenAI", "GPT-5", "Claude"])
        assert "OpenAI" in sa.core_entities


# ── DailyReport ───────────────────────────────────────────────────────────────

class TestDailyReport:
    def test_hot_events_carry_new_fields(self):
        ev = make_hot_event(
            background="背景",
            tags=["#AI"],
            reference_links=["资源1"],
        )
        report = make_daily_report(hot_events=[ev])
        assert report.hot_events[0].background == "背景"
        assert report.hot_events[0].tags == ["#AI"]
        assert report.hot_events[0].reference_links == ["资源1"]

    def test_model_dump_serializes_new_fields(self):
        report = make_daily_report()
        data = report.model_dump(mode="json")
        first_event = data["hot_events"][0]
        assert "background" in first_event
        assert "tags" in first_event
        assert "reference_links" in first_event

    def test_empty_hot_events_allowed(self):
        report = make_daily_report(hot_events=[])
        assert report.hot_events == []

    def test_report_date_stored(self):
        report = make_daily_report(report_date="2026-04-10")
        assert report.report_date == "2026-04-10"

    def test_article_counts_stored(self):
        report = make_daily_report(
            total_articles_processed=20,
            total_articles_after_filter=15,
        )
        assert report.total_articles_processed == 20
        assert report.total_articles_after_filter == 15

    def test_both_summaries_stored(self):
        report = make_daily_report(
            executive_summary_zh="今日摘要",
            executive_summary_en="Today's summary",
        )
        assert report.executive_summary_zh == "今日摘要"
        assert report.executive_summary_en == "Today's summary"


# ── DataFilterRules ───────────────────────────────────────────────────────────

class TestDataFilterRules:
    def test_defaults(self):
        rules = DataFilterRules()
        assert rules.top_k == 5
        assert rules.min_impact_score == 7
        assert rules.exclude_categories == []

    def test_custom_values(self):
        rules = DataFilterRules(top_k=3, min_impact_score=8, exclude_categories=["政策合规"])
        assert rules.top_k == 3
        assert rules.min_impact_score == 8
        assert "政策合规" in rules.exclude_categories
