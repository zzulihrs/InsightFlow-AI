"""Unit tests for storage layer: Markdown generation and Horizon-style HTML generation."""

import json

import pytest

from src.storage.html_generator import generate_html, _toc, _article_entry, _score_stars
from src.storage.store import _generate_markdown
from tests.conftest import make_daily_report, make_hot_event, make_scored_article


# ── _generate_markdown ────────────────────────────────────────────────────────

class TestGenerateMarkdown:
    def test_title_contains_report_date(self):
        report = make_daily_report(report_date="2026-04-10")
        md = _generate_markdown(report)
        assert "2026-04-10" in md

    def test_executive_summary_zh_included(self):
        report = make_daily_report(executive_summary_zh="今日重要发现汇总")
        md = _generate_markdown(report)
        assert "今日重要发现汇总" in md

    def test_executive_summary_en_included(self):
        report = make_daily_report(executive_summary_en="Key findings today")
        md = _generate_markdown(report)
        assert "Key findings today" in md

    def test_star_rating_format(self):
        """Hot events should use ⭐ X.0/10 format."""
        ev = make_hot_event(impact_score=9)
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "⭐ 9.0/10" in md

    def test_event_title_in_markdown(self):
        ev = make_hot_event(title="GPT-5 发布了")
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "GPT-5 发布了" in md

    def test_background_rendered_when_set(self):
        ev = make_hot_event(background="GPT 是 OpenAI 的核心模型系列")
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "GPT 是 OpenAI 的核心模型系列" in md
        assert "背景" in md

    def test_background_section_skipped_when_empty(self):
        ev = make_hot_event(background="")
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        # Should not have an empty Background: section
        assert "**背景：**\n\n\n" not in md

    def test_tags_rendered_when_set(self):
        ev = make_hot_event(tags=["#AI", "#OpenAI", "#LLM"])
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "#AI" in md
        assert "#OpenAI" in md

    def test_reference_links_rendered(self):
        ev = make_hot_event(reference_links=["OpenAI 博客 — GPT-5", "arXiv 论文"])
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "OpenAI 博客 — GPT-5" in md
        assert "arXiv 论文" in md

    def test_reference_links_section_skipped_when_empty(self):
        ev = make_hot_event(reference_links=[])
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "参考资源" not in md

    def test_multiple_events_all_appear(self):
        events = [
            make_hot_event(rank=1, title="事件一"),
            make_hot_event(rank=2, title="事件二"),
        ]
        report = make_daily_report(hot_events=events)
        md = _generate_markdown(report)
        assert "事件一" in md
        assert "事件二" in md

    def test_footer_contains_processed_count(self):
        report = make_daily_report(total_articles_processed=20)
        md = _generate_markdown(report)
        assert "20" in md

    def test_no_hot_events_skips_section(self):
        report = make_daily_report(hot_events=[])
        md = _generate_markdown(report)
        assert "Hot Events" not in md


# ── _score_stars ──────────────────────────────────────────────────────────────

class TestScoreStars:
    def test_format_is_star_decimal_slash_ten(self):
        assert _score_stars(8) == "⭐ 8.0/10"
        assert _score_stars(10) == "⭐ 10.0/10"
        assert _score_stars(1) == "⭐ 1.0/10"


# ── _toc ──────────────────────────────────────────────────────────────────────

class TestTOC:
    def test_empty_events_returns_empty_string(self):
        assert _toc([]) == ""

    def test_toc_contains_event_title(self):
        events = [{"rank": 1, "title": "GPT-5 发布", "impact_score": 9}]
        toc_html = _toc(events)
        assert "GPT-5 发布" in toc_html

    def test_toc_contains_anchor_links(self):
        events = [{"rank": 2, "title": "Claude 4", "impact_score": 8}]
        toc_html = _toc(events)
        assert 'href="#article-2"' in toc_html

    def test_toc_shows_star_score(self):
        events = [{"rank": 1, "title": "测试", "impact_score": 7}]
        toc_html = _toc(events)
        assert "⭐" in toc_html
        assert "7.0" in toc_html

    def test_toc_class_present(self):
        events = [{"rank": 1, "title": "测试", "impact_score": 9}]
        toc_html = _toc(events)
        assert 'class="toc"' in toc_html

    def test_multiple_events_all_in_toc(self):
        events = [
            {"rank": 1, "title": "事件一", "impact_score": 9},
            {"rank": 2, "title": "事件二", "impact_score": 8},
            {"rank": 3, "title": "事件三", "impact_score": 7},
        ]
        toc_html = _toc(events)
        assert "事件一" in toc_html
        assert "事件二" in toc_html
        assert "事件三" in toc_html


# ── generate_html (Horizon style) ─────────────────────────────────────────────

class TestGenerateHTML:
    def _make_report_dict(self, events=None, **kwargs):
        report = make_daily_report(hot_events=events, **kwargs)
        return json.loads(report.model_dump_json())

    def _make_scored_list(self):
        sa = make_scored_article(original_url="https://openai.com/gpt-5")
        return [json.loads(sa.model_dump_json())]

    def test_valid_html_doctype(self):
        report_dict = self._make_report_dict()
        html = generate_html("2026-04-10", report_dict, [])
        assert html.startswith("<!DOCTYPE html>")

    def test_lang_attribute_is_zh_cn(self):
        report_dict = self._make_report_dict()
        html = generate_html("2026-04-10", report_dict, [])
        assert 'lang="zh-CN"' in html

    def test_report_date_in_title_tag(self):
        report_dict = self._make_report_dict()
        html = generate_html("2026-04-10", report_dict, [])
        assert "2026-04-10" in html

    def test_toc_section_present(self):
        report_dict = self._make_report_dict()
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="toc"' in html

    def test_article_entry_present(self):
        report_dict = self._make_report_dict()
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="article-entry"' in html

    def test_event_title_rendered(self):
        ev = make_hot_event(title="Claude 4 正式发布")
        report_dict = self._make_report_dict(events=[ev])
        html = generate_html("2026-04-10", report_dict, [])
        assert "Claude 4 正式发布" in html

    def test_score_pill_rendered(self):
        ev = make_hot_event(impact_score=8)
        report_dict = self._make_report_dict(events=[ev])
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="score-pill"' in html
        assert "⭐ 8.0/10" in html

    def test_background_section_rendered_when_set(self):
        ev = make_hot_event(background="这是背景信息说明")
        report_dict = self._make_report_dict(events=[ev])
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="article-background"' in html
        assert "这是背景信息说明" in html

    def test_background_section_absent_when_empty(self):
        ev = make_hot_event(background="")
        report_dict = self._make_report_dict(events=[ev])
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="article-background"' not in html

    def test_tags_rendered_when_set(self):
        ev = make_hot_event(tags=["#AI", "#LLM", "#OpenAI"])
        report_dict = self._make_report_dict(events=[ev])
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="tags-row"' in html
        assert "#AI" in html
        assert "#LLM" in html

    def test_tags_absent_when_empty(self):
        ev = make_hot_event(tags=[])
        report_dict = self._make_report_dict(events=[ev])
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="tags-row"' not in html

    def test_reference_links_rendered_when_set(self):
        ev = make_hot_event(reference_links=["OpenAI 博客", "论文链接"])
        report_dict = self._make_report_dict(events=[ev])
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="ref-links"' in html
        assert "OpenAI 博客" in html

    def test_reference_links_absent_when_empty(self):
        ev = make_hot_event(reference_links=[])
        report_dict = self._make_report_dict(events=[ev])
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="ref-links"' not in html

    def test_meta_info_shows_article_count(self):
        report_dict = self._make_report_dict(total_articles_processed=20)
        html = generate_html("2026-04-10", report_dict, [])
        assert "20" in html

    def test_executive_summary_rendered(self):
        report_dict = self._make_report_dict(executive_summary_zh="今日摘要内容")
        html = generate_html("2026-04-10", report_dict, [])
        assert "今日摘要内容" in html

    def test_no_echarts_script(self):
        """Horizon-style page should not include old dashboard ECharts library."""
        report_dict = self._make_report_dict()
        html = generate_html("2026-04-10", report_dict, [])
        assert "echarts" not in html

    def test_noto_serif_font_in_css(self):
        """Horizon-style uses Noto Serif SC for typography."""
        report_dict = self._make_report_dict()
        html = generate_html("2026-04-10", report_dict, [])
        assert "Noto Serif SC" in html

    def test_html_escaping_in_title(self):
        """Titles with special HTML chars must be escaped."""
        ev = make_hot_event(title="GPT<5> & 'Model'")
        report_dict = self._make_report_dict(events=[ev])
        html = generate_html("2026-04-10", report_dict, [])
        # Raw unescaped < must not appear inside HTML content
        assert "<5>" not in html
        assert "&lt;5&gt;" in html

    def test_article_anchor_ids_present(self):
        ev1 = make_hot_event(rank=1)
        ev2 = make_hot_event(rank=2)
        report_dict = self._make_report_dict(events=[ev1, ev2])
        html = generate_html("2026-04-10", report_dict, [])
        assert 'id="article-1"' in html
        assert 'id="article-2"' in html

    def test_source_link_rendered_from_scored_map(self):
        """When scored article URL is available, it should appear in the entry."""
        ev = make_hot_event(title="GPT-5 正式发布", source_url="https://openai.com/gpt-5")
        report_dict = self._make_report_dict(events=[ev])
        scored = self._make_scored_list()
        html = generate_html("2026-04-10", report_dict, scored)
        assert "https://openai.com/gpt-5" in html

    def test_empty_hot_events_still_valid_html(self):
        report_dict = self._make_report_dict(events=[])
        html = generate_html("2026-04-10", report_dict, [])
        assert "<!DOCTYPE html>" in html
        assert "</html>" in html

    def test_footer_contains_generation_metadata(self):
        report_dict = self._make_report_dict(
            total_articles_processed=20,
            total_articles_after_filter=15,
        )
        html = generate_html("2026-04-10", report_dict, [])
        assert 'class="page-footer"' in html
        assert "20" in html
        assert "15" in html


# ── Horizon style specifics ───────────────────────────────────────────────────

class TestHorizonStyleLayout:
    """Verify the page matches Horizon digest style vs old dashboard."""

    def _html(self, **kwargs):
        report = make_daily_report(**kwargs)
        report_dict = json.loads(report.model_dump_json())
        return generate_html("2026-04-10", report_dict, [])

    def test_no_tab_navigation(self):
        """Old dashboard had tab-nav; Horizon page doesn't."""
        html = self._html()
        assert 'class="tab-nav"' not in html
        assert 'class="tab-btn"' not in html

    def test_no_kpi_grid(self):
        """Old dashboard had KPI cards; Horizon page doesn't."""
        html = self._html()
        assert 'class="kpi-grid"' not in html

    def test_has_site_header(self):
        html = self._html()
        assert 'class="site-header"' in html

    def test_has_page_wrapper(self):
        html = self._html()
        assert 'class="page-wrapper"' in html

    def test_byline_shows_category(self):
        ev = make_hot_event(category="产品发布")
        report = make_daily_report(hot_events=[ev])
        html = generate_html("2026-04-10", json.loads(report.model_dump_json()), [])
        assert "产品发布" in html
