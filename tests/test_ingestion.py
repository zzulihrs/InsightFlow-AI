"""Unit tests for ingestion pipeline: clean, dedup."""

from datetime import datetime

import pytest

from src.ingestion.cleaner import clean_text, clean_articles
from src.ingestion.dedup import _jaccard, _tokenize, deduplicate
from tests.conftest import make_raw_article


# ── clean_text ────────────────────────────────────────────────────────────────

class TestCleanText:
    def test_removes_html_tags(self):
        assert clean_text("<b>Hello</b>") == "Hello"

    def test_removes_nested_html(self):
        assert clean_text("<div><p>内容</p></div>") == "内容"

    def test_collapses_multiple_spaces(self):
        assert clean_text("hello   world") == "hello world"

    def test_collapses_newlines(self):
        assert clean_text("line1\n\nline2") == "line1 line2"

    def test_collapses_tabs(self):
        assert clean_text("col1\t\tcol2") == "col1 col2"

    def test_strips_leading_trailing_whitespace(self):
        assert clean_text("  text  ") == "text"

    def test_empty_string_returns_empty(self):
        assert clean_text("") == ""

    def test_no_html_unchanged(self):
        assert clean_text("普通文本") == "普通文本"

    def test_html_with_attributes(self):
        assert clean_text('<a href="http://example.com">链接</a>') == "链接"

    def test_mixed_html_and_whitespace(self):
        result = clean_text("  <b>bold</b>  and  <i>italic</i>  ")
        assert result == "bold and italic"


# ── clean_articles ────────────────────────────────────────────────────────────

class TestCleanArticles:
    def test_cleans_title_and_content(self):
        article = make_raw_article(
            title="<b>OpenAI</b> 发布",
            content="正文  内容\n有 <br/> HTML",
        )
        result = clean_articles([article])
        assert result[0].title == "OpenAI 发布"
        assert result[0].content == "正文 内容 有 HTML"

    def test_does_not_mutate_original(self):
        article = make_raw_article(title="<b>原始</b>")
        original_title = article.title
        clean_articles([article])
        assert article.title == original_title  # original untouched

    def test_returns_same_length_list(self):
        articles = [make_raw_article(title=f"文章{i}") for i in range(5)]
        result = clean_articles(articles)
        assert len(result) == 5

    def test_empty_list_returns_empty(self):
        assert clean_articles([]) == []

    def test_preserves_other_fields(self):
        article = make_raw_article(source_name="TestSource", source_weight=1.8)
        result = clean_articles([article])
        assert result[0].source_name == "TestSource"
        assert result[0].source_weight == 1.8


# ── _jaccard ──────────────────────────────────────────────────────────────────

class TestJaccard:
    def test_identical_sets_return_one(self):
        s = {"a", "b", "c"}
        assert _jaccard(s, s) == 1.0

    def test_disjoint_sets_return_zero(self):
        assert _jaccard({"a"}, {"b"}) == 0.0

    def test_both_empty_return_one(self):
        assert _jaccard(set(), set()) == 1.0

    def test_partial_overlap(self):
        # intersection=1, union=3 → 1/3
        result = _jaccard({"a", "b"}, {"b", "c"})
        assert abs(result - 1 / 3) < 1e-9

    def test_one_subset_of_other(self):
        # intersection=1, union=2 → 0.5
        assert _jaccard({"a"}, {"a", "b"}) == 0.5


# ── _tokenize ─────────────────────────────────────────────────────────────────

class TestTokenize:
    def test_english_lowercases_and_splits(self):
        tokens = _tokenize("Hello World", "en")
        assert "hello" in tokens
        assert "world" in tokens

    def test_chinese_uses_jieba(self):
        tokens = _tokenize("人工智能", "zh")
        assert isinstance(tokens, set)
        assert len(tokens) >= 1  # jieba produces at least one token

    def test_empty_english_title(self):
        tokens = _tokenize("", "en")
        # split("") gives [''] which is {''} but jieba gives set()
        assert isinstance(tokens, set)


# ── deduplicate ───────────────────────────────────────────────────────────────

class TestDeduplicate:
    def test_empty_list_returns_empty(self):
        assert deduplicate([]) == []

    def test_single_article_returned_as_is(self):
        a = make_raw_article()
        result = deduplicate([a])
        assert len(result) == 1

    def test_unique_articles_all_kept(self):
        articles = [
            make_raw_article(title="OpenAI 发布 GPT-5"),
            make_raw_article(title="Anthropic 发布 Claude 4"),
            make_raw_article(title="Google 发布 Gemini Ultra"),
        ]
        result = deduplicate(articles)
        assert len(result) == 3

    def test_near_duplicate_removed(self):
        # Same title → Jaccard ≈ 1.0 > 0.80
        articles = [
            make_raw_article(title="OpenAI releases GPT-5", language="en", source_weight=1.0),
            make_raw_article(title="OpenAI releases GPT-5", language="en", source_weight=1.5),
        ]
        result = deduplicate(articles)
        assert len(result) == 1

    def test_keeps_higher_weight_on_duplicate(self):
        articles = [
            make_raw_article(title="OpenAI releases GPT-5", language="en", source_weight=1.0),
            make_raw_article(title="OpenAI releases GPT-5", language="en", source_weight=2.0),
        ]
        result = deduplicate(articles)
        assert result[0].source_weight == 2.0

    def test_high_threshold_keeps_similar(self):
        # "OpenAI GPT" vs "OpenAI GPT-5" — overlap 2/3 ≈ 0.67 < 0.80, should keep both
        articles = [
            make_raw_article(title="OpenAI GPT update released", language="en"),
            make_raw_article(title="Anthropic Claude update released", language="en"),
        ]
        result = deduplicate(articles, threshold=0.80)
        assert len(result) == 2

    def test_all_duplicates_leaves_one(self):
        articles = [make_raw_article(title="same title", language="en")] * 4
        result = deduplicate(articles)
        assert len(result) == 1
