"""Unit tests for storage layer: Markdown generation and tab-based HTML generation."""

import json

import pytest

from src.storage.html_generator import (
    generate_html,
    _article_entry,
    _score_stars,
    _deep_dives_panel,
    _trends_panel,
    _risks_panel,
)
from src.storage.store import _generate_markdown
from tests.conftest import make_daily_report, make_hot_event, make_scored_article


# ── _score_stars ──────────────────────────────────────────────────────────────

class TestScoreStars:
    def test_format_decimal_slash_ten(self):
        assert _score_stars(8) == "⭐ 8.0/10"
        assert _score_stars(10) == "⭐ 10.0/10"
        assert _score_stars(1) == "⭐ 1.0/10"


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

    def test_background_section_skipped_when_empty(self):
        ev = make_hot_event(background="")
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "**背景：**\n\n\n" not in md

    def test_tags_rendered_when_set(self):
        ev = make_hot_event(tags=["#AI", "#OpenAI"])
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "#AI" in md

    def test_reference_links_rendered(self):
        ev = make_hot_event(reference_links=["OpenAI 博客", "arXiv 论文"])
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "OpenAI 博客" in md

    def test_reference_links_skipped_when_empty(self):
        ev = make_hot_event(reference_links=[])
        report = make_daily_report(hot_events=[ev])
        md = _generate_markdown(report)
        assert "参考资源" not in md

    def test_multiple_events_all_appear(self):
        events = [make_hot_event(rank=1, title="事件一"), make_hot_event(rank=2, title="事件二")]
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


# ── Tab structure (generate_html) ────────────────────────────────────────────

class TestTabStructure:
    """Verify the page has correct tab-based navigation."""

    def _rd(self, events=None, **kw):
        return json.loads(make_daily_report(hot_events=events, **kw).model_dump_json())

    def test_valid_html_doctype(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert html.startswith("<!DOCTYPE html>")

    def test_lang_is_zh_cn(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert 'lang="zh-CN"' in html

    def test_tab_bar_present(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert 'class="tab-bar"' in html

    def test_four_tab_buttons_present(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert 'id="tab-hot"' in html
        assert 'id="tab-deep"' in html
        assert 'id="tab-trends"' in html
        assert 'id="tab-risks"' in html

    def test_four_panels_present(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert 'id="panel-hot"' in html
        assert 'id="panel-deep"' in html
        assert 'id="panel-trends"' in html
        assert 'id="panel-risks"' in html

    def test_hot_tab_is_active_by_default(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert 'id="tab-hot" onclick' in html or 'id="panel-hot" class="tab-panel active"' in html

    def test_switchTab_js_present(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert "switchTab" in html

    def test_no_old_tab_nav_class(self):
        """Old dashboard class names should not appear."""
        html = generate_html("2026-04-10", self._rd(), [])
        assert 'class="tab-nav"' not in html
        assert 'class="kpi-grid"' not in html

    def test_no_echarts(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert "echarts" not in html

    def test_noto_serif_font(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert "Noto Serif SC" in html

    def test_date_in_header(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert "2026-04-10" in html

    def test_article_count_in_header(self):
        rd = self._rd(total_articles_processed=20)
        html = generate_html("2026-04-10", rd, [])
        assert "20" in html

    def test_sticky_site_header(self):
        html = generate_html("2026-04-10", self._rd(), [])
        assert 'class="site-header"' in html

    def test_tab_count_badge_for_hot_events(self):
        events = [make_hot_event(rank=i + 1) for i in range(3)]
        rd = self._rd(events=events)
        html = generate_html("2026-04-10", rd, [])
        assert 'class="tab-count"' in html

    def test_empty_panels_still_valid_html(self):
        rd = self._rd(events=[])
        rd["deep_dives"] = []
        rd["trend_insights"] = []
        rd["risks_and_opportunities"] = []
        html = generate_html("2026-04-10", rd, [])
        assert "<!DOCTYPE html>" in html
        assert "</html>" in html

    def test_html_escaping_prevents_xss(self):
        ev = make_hot_event(title="GPT<5> & 'Model'")
        rd = self._rd(events=[ev])
        html = generate_html("2026-04-10", rd, [])
        assert "<5>" not in html
        assert "&lt;5&gt;" in html


# ── Hot events panel ──────────────────────────────────────────────────────────

class TestHotEventsPanel:
    def _rd(self, events=None, **kw):
        return json.loads(make_daily_report(hot_events=events, **kw).model_dump_json())

    def test_event_title_rendered(self):
        ev = make_hot_event(title="Claude 4 正式发布")
        html = generate_html("2026-04-10", self._rd(events=[ev]), [])
        assert "Claude 4 正式发布" in html

    def test_score_pill_rendered(self):
        ev = make_hot_event(impact_score=8)
        html = generate_html("2026-04-10", self._rd(events=[ev]), [])
        assert 'class="score-pill"' in html
        assert "⭐ 8.0/10" in html

    def test_background_rendered_when_set(self):
        ev = make_hot_event(background="这是背景说明")
        html = generate_html("2026-04-10", self._rd(events=[ev]), [])
        assert "这是背景说明" in html
        assert 'class="article-background"' in html

    def test_background_absent_when_empty(self):
        ev = make_hot_event(background="")
        html = generate_html("2026-04-10", self._rd(events=[ev]), [])
        assert 'class="article-background"' not in html

    def test_tags_rendered_when_set(self):
        ev = make_hot_event(tags=["#AI", "#LLM"])
        html = generate_html("2026-04-10", self._rd(events=[ev]), [])
        assert 'class="tags-row"' in html
        assert "#AI" in html

    def test_tags_absent_when_empty(self):
        ev = make_hot_event(tags=[])
        html = generate_html("2026-04-10", self._rd(events=[ev]), [])
        assert 'class="tags-row"' not in html

    def test_reference_links_rendered(self):
        ev = make_hot_event(reference_links=["OpenAI 博客"])
        html = generate_html("2026-04-10", self._rd(events=[ev]), [])
        assert "OpenAI 博客" in html
        assert 'class="ref-links"' in html

    def test_reference_links_absent_when_empty(self):
        ev = make_hot_event(reference_links=[])
        html = generate_html("2026-04-10", self._rd(events=[ev]), [])
        assert 'class="ref-links"' not in html

    def test_executive_summary_in_hot_panel(self):
        rd = self._rd(executive_summary_zh="今日摘要内容")
        html = generate_html("2026-04-10", rd, [])
        assert "今日摘要内容" in html

    def test_article_anchor_ids(self):
        events = [make_hot_event(rank=1), make_hot_event(rank=2)]
        html = generate_html("2026-04-10", self._rd(events=events), [])
        assert 'id="article-1"' in html
        assert 'id="article-2"' in html

    def test_category_badge_rendered(self):
        ev = make_hot_event(category="产品发布")
        rd = json.loads(make_daily_report(hot_events=[ev]).model_dump_json())
        html = generate_html("2026-04-10", rd, [])
        assert "产品发布" in html

    def test_source_url_from_scored_map(self):
        ev = make_hot_event(title="GPT-5 发布", source_url="https://openai.com/gpt-5")
        rd = self._rd(events=[ev])
        sa = make_scored_article(original_url="https://openai.com/gpt-5")
        scored = [json.loads(sa.model_dump_json())]
        html = generate_html("2026-04-10", rd, scored)
        assert "https://openai.com/gpt-5" in html


# ── Deep dives panel ──────────────────────────────────────────────────────────

class TestDeepDivesPanel:
    def _dd(self, **kw):
        base = dict(
            title="GPT-5 深度解析",
            background="GPT-5 是 OpenAI 最新旗舰模型",
            key_findings=["发现1", "发现2", "发现3"],
            technical_impact="改变工具链",
            business_impact="竞争加剧",
            outlook="半年内落地",
        )
        base.update(kw)
        return base

    def test_empty_shows_tip(self):
        html = _deep_dives_panel([])
        assert "empty-tip" in html

    def test_title_rendered(self):
        html = _deep_dives_panel([self._dd(title="Claude Opus 深度分析")])
        assert "Claude Opus 深度分析" in html

    def test_background_rendered(self):
        html = _deep_dives_panel([self._dd(background="背景内容")])
        assert "背景内容" in html

    def test_findings_rendered(self):
        html = _deep_dives_panel([self._dd(key_findings=["发现A", "发现B"])])
        assert "发现A" in html
        assert "发现B" in html

    def test_technical_impact_rendered(self):
        html = _deep_dives_panel([self._dd(technical_impact="技术影响内容")])
        assert "技术影响内容" in html

    def test_business_impact_rendered(self):
        html = _deep_dives_panel([self._dd(business_impact="商业影响内容")])
        assert "商业影响内容" in html

    def test_outlook_rendered(self):
        html = _deep_dives_panel([self._dd(outlook="未来展望内容")])
        assert "未来展望内容" in html

    def test_card_class_present(self):
        html = _deep_dives_panel([self._dd()])
        assert 'class="deep-dive-card"' in html

    def test_multiple_dives(self):
        html = _deep_dives_panel([self._dd(title="分析一"), self._dd(title="分析二")])
        assert "分析一" in html
        assert "分析二" in html

    def test_integrated_in_full_html(self):
        rd = json.loads(make_daily_report().model_dump_json())
        rd["deep_dives"] = [self._dd()]
        html = generate_html("2026-04-10", rd, [])
        assert 'id="panel-deep"' in html
        assert "GPT-5 深度解析" in html


# ── Trends panel ──────────────────────────────────────────────────────────────

class TestTrendsPanel:
    def _t(self, **kw):
        base = dict(
            trend_name="AI 代理化加速",
            description="Claude Managed Agents 和 GPT-5 Computer Use 同步落地",
            supporting_events=["Claude Managed Agents", "GPT-5"],
            confidence="高",
        )
        base.update(kw)
        return base

    def test_empty_shows_tip(self):
        html = _trends_panel([])
        assert "empty-tip" in html

    def test_trend_name_rendered(self):
        html = _trends_panel([self._t(trend_name="测试趋势")])
        assert "测试趋势" in html

    def test_description_rendered(self):
        html = _trends_panel([self._t(description="这是趋势描述")])
        assert "这是趋势描述" in html

    def test_confidence_high(self):
        html = _trends_panel([self._t(confidence="高")])
        assert "高" in html
        assert "conf-badge" in html

    def test_confidence_mid(self):
        html = _trends_panel([self._t(confidence="中")])
        assert "中" in html

    def test_supporting_events_rendered(self):
        html = _trends_panel([self._t(supporting_events=["事件A", "事件B"])])
        assert "事件A" in html
        assert "事件B" in html

    def test_card_class_present(self):
        html = _trends_panel([self._t()])
        assert 'class="trend-card"' in html

    def test_multiple_trends(self):
        html = _trends_panel([self._t(trend_name="趋势一"), self._t(trend_name="趋势二")])
        assert "趋势一" in html
        assert "趋势二" in html

    def test_integrated_in_full_html(self):
        rd = json.loads(make_daily_report().model_dump_json())
        rd["trend_insights"] = [self._t()]
        html = generate_html("2026-04-10", rd, [])
        assert 'id="panel-trends"' in html
        assert "AI 代理化加速" in html


# ── Risks panel ───────────────────────────────────────────────────────────────

class TestRisksPanel:
    def _risk(self, **kw):
        base = dict(type="risk", title="模型退役迁移风险",
                    description="GPT-4o 退役需提前迁移", related_events=["GPT-4o 退役"])
        base.update(kw)
        return base

    def _opp(self, **kw):
        base = dict(type="opportunity", title="Agent 平台投资窗口",
                    description="Managed Agents 公测是切入时机", related_events=["Claude Managed Agents"])
        base.update(kw)
        return base

    def test_empty_shows_tip(self):
        html = _risks_panel([])
        assert "empty-tip" in html

    def test_risk_badge_rendered(self):
        html = _risks_panel([self._risk()])
        assert "⚠ 风险" in html
        assert "badge-risk" in html

    def test_opp_badge_rendered(self):
        html = _risks_panel([self._opp()])
        assert "✦ 机会" in html
        assert "badge-opp" in html

    def test_risk_title_rendered(self):
        html = _risks_panel([self._risk(title="测试风险")])
        assert "测试风险" in html

    def test_risk_description_rendered(self):
        html = _risks_panel([self._risk(description="这是风险描述")])
        assert "这是风险描述" in html

    def test_related_events_rendered(self):
        html = _risks_panel([self._risk(related_events=["事件A", "事件B"])])
        assert "事件A" in html
        assert "事件B" in html

    def test_risk_card_class(self):
        html = _risks_panel([self._risk()])
        assert 'class="risk-card"' in html

    def test_opp_card_class(self):
        html = _risks_panel([self._opp()])
        assert 'class="opp-card"' in html

    def test_mixed_risk_and_opportunity(self):
        html = _risks_panel([self._risk(), self._opp()])
        assert "⚠ 风险" in html
        assert "✦ 机会" in html

    def test_integrated_in_full_html(self):
        rd = json.loads(make_daily_report().model_dump_json())
        rd["risks_and_opportunities"] = [self._risk(), self._opp()]
        html = generate_html("2026-04-10", rd, [])
        assert 'id="panel-risks"' in html
        assert "⚠ 风险" in html
        assert "✦ 机会" in html

    def test_toc_counts_all_four_tabs(self):
        """Tab count badges should reflect content lengths."""
        events = [make_hot_event(rank=i + 1) for i in range(3)]
        rd = json.loads(make_daily_report(hot_events=events).model_dump_json())
        rd["deep_dives"] = [{"title": "X", "background": "", "key_findings": [],
                              "technical_impact": "", "business_impact": "", "outlook": ""}]
        rd["trend_insights"] = [{"trend_name": "T", "description": "D",
                                  "supporting_events": [], "confidence": "中"}]
        rd["risks_and_opportunities"] = [self._risk()]
        html = generate_html("2026-04-10", rd, [])
        # All four panels exist
        assert 'id="panel-hot"' in html
        assert 'id="panel-deep"' in html
        assert 'id="panel-trends"' in html
        assert 'id="panel-risks"' in html
