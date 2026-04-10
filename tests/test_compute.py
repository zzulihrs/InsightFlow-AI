"""Unit tests for compute pipeline: scorer, filter, cluster."""

import pytest

from src.compute.scorer import compute_scores
from src.compute.filter import filter_articles
from src.compute.cluster import cluster_articles, build_filtered_context
from src.models.article import ArticleCategory
from src.models.report import DataFilterRules
from tests.conftest import make_scored_article, make_data_filter_rules


# ── compute_scores ────────────────────────────────────────────────────────────

class TestComputeScores:
    """
    Scoring formula:
        raw = novelty*0.35 + impact*0.45 + readiness*0.20
        impact_score = clamp(round(raw * 2), 1, 10)
        final_score  = impact_score * source_weight
    """

    def test_formula_all_fives(self):
        # raw = 5*0.35 + 5*0.45 + 5*0.20 = 5.0  → round(5*2)=10
        sa = make_scored_article(novelty=5, impact=5, readiness=5, source_weight=1.0)
        compute_scores([sa])
        assert sa.impact_score == 10
        assert sa.final_score == 10.0

    def test_formula_all_ones(self):
        # raw = 1*0.35 + 1*0.45 + 1*0.20 = 1.0  → round(1*2)=2
        sa = make_scored_article(novelty=1, impact=1, readiness=1, source_weight=1.0)
        compute_scores([sa])
        assert sa.impact_score == 2

    def test_formula_mixed(self):
        # raw = 3*0.35 + 4*0.45 + 2*0.20 = 1.05+1.80+0.40 = 3.25 → round(6.5)=6 (or 7 depending on banker's rounding)
        sa = make_scored_article(novelty=3, impact=4, readiness=2, source_weight=1.0)
        compute_scores([sa])
        # round(3.25*2) = round(6.5) = 6 or 7 (Python uses banker's rounding → 6)
        assert sa.impact_score in (6, 7)

    def test_clamp_max_at_ten(self):
        sa = make_scored_article(novelty=5, impact=5, readiness=5, source_weight=2.0)
        compute_scores([sa])
        assert sa.impact_score <= 10

    def test_clamp_min_at_one(self):
        sa = make_scored_article(novelty=1, impact=1, readiness=1, source_weight=1.0)
        compute_scores([sa])
        assert sa.impact_score >= 1

    def test_source_weight_multiplied_into_final_score(self):
        sa = make_scored_article(novelty=5, impact=5, readiness=5, source_weight=1.5)
        compute_scores([sa])
        assert sa.final_score == sa.impact_score * 1.5

    def test_source_weight_overridden_from_dict(self):
        sa = make_scored_article(source_name="OpenAI Blog", source_weight=1.0)
        compute_scores([sa], source_weights={"OpenAI Blog": 2.0})
        assert sa.source_weight == 2.0

    def test_source_weight_not_overridden_if_name_missing(self):
        sa = make_scored_article(source_name="Unknown", source_weight=1.0)
        compute_scores([sa], source_weights={"OpenAI Blog": 2.0})
        assert sa.source_weight == 1.0

    def test_returns_same_list_object(self):
        articles = [make_scored_article()]
        result = compute_scores(articles)
        assert result is articles

    def test_empty_list_returns_empty(self):
        result = compute_scores([])
        assert result == []

    def test_multiple_articles_all_scored(self):
        articles = [
            make_scored_article(novelty=3, impact=3, readiness=3),
            make_scored_article(novelty=5, impact=5, readiness=5),
        ]
        compute_scores(articles)
        assert all(a.impact_score >= 1 for a in articles)
        assert articles[1].impact_score >= articles[0].impact_score


# ── filter_articles ───────────────────────────────────────────────────────────

class TestFilterArticles:
    def _make_article_with_score(self, impact_score, final_score=None, cat=None):
        sa = make_scored_article(
            category=cat or ArticleCategory.PRODUCT_RELEASE,
            impact_score=impact_score,
            final_score=final_score if final_score is not None else float(impact_score),
        )
        return sa

    def test_filters_below_min_impact_score(self):
        articles = [
            self._make_article_with_score(9),
            self._make_article_with_score(6),  # below threshold=7
            self._make_article_with_score(7),
        ]
        rules = make_data_filter_rules(min_impact_score=7, top_k=10)
        top, filtered = filter_articles(articles, rules)
        assert all(a.impact_score >= 7 for a in filtered)
        assert len(filtered) == 2

    def test_respects_top_k(self):
        articles = [self._make_article_with_score(9) for _ in range(10)]
        rules = make_data_filter_rules(top_k=3, min_impact_score=1)
        top, _ = filter_articles(articles, rules)
        assert len(top) <= 3

    def test_sorts_by_final_score_descending(self):
        articles = [
            self._make_article_with_score(7, final_score=7.0),
            self._make_article_with_score(9, final_score=9.0),
            self._make_article_with_score(8, final_score=8.0),
        ]
        rules = make_data_filter_rules(top_k=10, min_impact_score=1)
        _, filtered = filter_articles(articles, rules)
        scores = [a.final_score for a in filtered]
        assert scores == sorted(scores, reverse=True)

    def test_excludes_specified_categories(self):
        articles = [
            self._make_article_with_score(9, cat=ArticleCategory.POLICY_COMPLIANCE),
            self._make_article_with_score(9, cat=ArticleCategory.TECH_BREAKTHROUGH),
        ]
        rules = make_data_filter_rules(
            min_impact_score=1,
            top_k=10,
            exclude_categories=["政策合规"],
        )
        _, filtered = filter_articles(articles, rules)
        cats = [a.category.value for a in filtered]
        assert "政策合规" not in cats

    def test_top_events_is_subset_of_filtered(self):
        articles = [self._make_article_with_score(9) for _ in range(8)]
        rules = make_data_filter_rules(top_k=3, min_impact_score=1)
        top, filtered = filter_articles(articles, rules)
        assert len(top) <= len(filtered)
        for ev in top:
            assert ev in filtered

    def test_empty_list_returns_empty_tuples(self):
        rules = make_data_filter_rules()
        top, filtered = filter_articles([], rules)
        assert top == []
        assert filtered == []

    def test_all_below_threshold_returns_empty(self):
        articles = [self._make_article_with_score(3) for _ in range(5)]
        rules = make_data_filter_rules(min_impact_score=8)
        top, filtered = filter_articles(articles, rules)
        assert top == []
        assert filtered == []


# ── cluster_articles ──────────────────────────────────────────────────────────

class TestClusterArticles:
    def test_groups_by_category(self):
        articles = [
            make_scored_article(category=ArticleCategory.TECH_BREAKTHROUGH),
            make_scored_article(category=ArticleCategory.TECH_BREAKTHROUGH),
            make_scored_article(category=ArticleCategory.PRODUCT_RELEASE),
        ]
        clusters, _ = cluster_articles(articles)
        assert "技术突破" in clusters
        assert "产品发布" in clusters
        assert len(clusters["技术突破"]) == 2
        assert len(clusters["产品发布"]) == 1

    def test_entity_frequency_counted(self):
        articles = [
            make_scored_article(core_entities=["OpenAI", "GPT-5"]),
            make_scored_article(core_entities=["OpenAI", "Claude"]),
            make_scored_article(core_entities=["Anthropic"]),
        ]
        _, entity_freq = cluster_articles(articles)
        freq_map = dict(entity_freq)
        assert freq_map["OpenAI"] == 2
        assert freq_map.get("GPT-5", 0) == 1
        assert freq_map.get("Anthropic", 0) == 1

    def test_entity_frequency_max_ten(self):
        # Create multiple articles so total distinct entities exceed 10
        # Each article can have at most 10 entities (model constraint)
        articles = [
            make_scored_article(core_entities=[f"E{i}" for i in range(0, 7)]),
            make_scored_article(core_entities=[f"E{i}" for i in range(5, 12)]),
            make_scored_article(core_entities=[f"E{i}" for i in range(9, 16)]),
        ]
        _, entity_freq = cluster_articles(articles)
        assert len(entity_freq) <= 10

    def test_empty_list_returns_empty(self):
        clusters, entity_freq = cluster_articles([])
        assert clusters == {}
        assert entity_freq == []

    def test_single_article(self):
        article = make_scored_article(category=ArticleCategory.BUSINESS_CAPITAL)
        clusters, _ = cluster_articles([article])
        assert "商业资本" in clusters


# ── build_filtered_context ────────────────────────────────────────────────────

class TestBuildFilteredContext:
    def _scored_batch(self, n=5, novelty=4, impact=4, readiness=4):
        return [make_scored_article(novelty=novelty, impact=impact, readiness=readiness)
                for _ in range(n)]

    def test_total_before_filter_correct(self):
        articles = self._scored_batch(6)
        rules = make_data_filter_rules(top_k=3, min_impact_score=1)
        ctx = build_filtered_context(articles, rules)
        assert ctx.total_before_filter == 6

    def test_total_after_filter_lte_before(self):
        articles = self._scored_batch(6)
        rules = make_data_filter_rules(top_k=3, min_impact_score=1)
        ctx = build_filtered_context(articles, rules)
        assert ctx.total_after_filter <= ctx.total_before_filter

    def test_top_events_lte_top_k(self):
        articles = self._scored_batch(10)
        rules = make_data_filter_rules(top_k=4, min_impact_score=1)
        ctx = build_filtered_context(articles, rules)
        assert len(ctx.top_events) <= 4

    def test_clusters_populated(self):
        articles = self._scored_batch(4)
        rules = make_data_filter_rules(min_impact_score=1, top_k=10)
        ctx = build_filtered_context(articles, rules)
        assert len(ctx.clusters) >= 1

    def test_entity_frequency_populated(self):
        articles = self._scored_batch(3)
        rules = make_data_filter_rules(min_impact_score=1, top_k=10)
        ctx = build_filtered_context(articles, rules)
        assert len(ctx.entity_frequency) >= 1

    def test_source_weights_applied(self):
        articles = self._scored_batch(2)
        rules = make_data_filter_rules(min_impact_score=1, top_k=10)
        ctx = build_filtered_context(articles, rules, source_weights={"OpenAI Blog": 1.5})
        # Articles with source_name="OpenAI Blog" should have weight applied
        for ev in ctx.all_filtered:
            if ev.source_name == "OpenAI Blog":
                assert ev.source_weight == 1.5

    def test_empty_articles_returns_empty_context(self):
        rules = make_data_filter_rules()
        ctx = build_filtered_context([], rules)
        assert ctx.total_before_filter == 0
        assert ctx.total_after_filter == 0
        assert ctx.top_events == []
