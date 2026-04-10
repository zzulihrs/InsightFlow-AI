"""HTML report generator — Horizon-style long-form digest page.

Page structure (four canonical sections):
  1. 今日AI领域主要热点   — hot_events
  2. 重要事件深度总结     — deep_dives
  3. 趋势判断             — trend_insights
  4. 风险或机会提示       — risks_and_opportunities
"""

import json
import html as html_lib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "output"


def _esc(text: str) -> str:
    return html_lib.escape(str(text or ""))


def _score_stars(score: int) -> str:
    return f"⭐ {score}.0/10"


# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """\
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

body {
  font-family: 'Noto Serif SC', 'Georgia', serif;
  background: #fafaf8;
  color: #1a1a1a;
  line-height: 1.8;
  font-size: 16px;
}

/* ── Page wrapper ── */
.page-wrapper {
  max-width: 780px;
  margin: 0 auto;
  padding: 3rem 1.5rem 6rem;
}

/* ── Site header ── */
.site-header {
  border-bottom: 2px solid #1a1a1a;
  padding-bottom: 1.5rem;
  margin-bottom: 2.5rem;
}
.site-name {
  font-family: 'Inter', sans-serif;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #666;
  margin-bottom: 0.5rem;
}
.report-title {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.2;
  margin-bottom: 0.6rem;
}
.report-subtitle {
  font-family: 'Inter', sans-serif;
  font-size: 0.92rem;
  color: #555;
  margin-bottom: 1rem;
}
.report-meta {
  font-family: 'Inter', sans-serif;
  font-size: 0.82rem;
  color: #888;
  background: #f0f0ec;
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
}

/* ── TOC ── */
.toc {
  background: #f5f5f0;
  border: 1px solid #e0e0d8;
  border-radius: 6px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 3rem;
}
.toc-title {
  font-family: 'Inter', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #888;
  margin-bottom: 0.85rem;
}
.toc-section {
  margin-bottom: 0.85rem;
}
.toc-section-name {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  color: #aaa;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 0.3rem;
}
.toc-list {
  list-style: none;
  padding: 0;
}
.toc-list li {
  padding: 0.2rem 0;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
}
.toc-list li:last-child { border-bottom: none; }
.toc-rank {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem;
  color: #aaa;
  min-width: 1.4rem;
}
.toc-list a {
  color: #1a1a1a;
  text-decoration: none;
  font-size: 0.88rem;
  line-height: 1.5;
}
.toc-list a:hover { text-decoration: underline; }
.toc-score {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  color: #aaa;
  margin-left: auto;
  white-space: nowrap;
}

/* ── Section heading ── */
.section-heading {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 3rem 0 1.5rem;
  padding-bottom: 0.6rem;
  border-bottom: 2px solid #1a1a1a;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.section-heading-icon {
  font-size: 1.1rem;
}

/* ── Hot event article entry ── */
.article-entry {
  margin-bottom: 3rem;
  padding-bottom: 2.5rem;
  border-bottom: 1px solid #d8d8d0;
}
.article-entry:last-child { border-bottom: none; }

.article-number {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #aaa;
  margin-bottom: 0.4rem;
}
.article-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.85rem;
}
.article-title {
  font-size: 1.3rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: -0.02em;
  flex: 1;
}
.article-title a { color: inherit; text-decoration: none; }
.article-title a:hover { text-decoration: underline; }
.score-pill {
  font-family: 'Inter', sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  white-space: nowrap;
  background: #fff8e6;
  border: 1px solid #f0d070;
  color: #7a5c00;
  padding: 0.3rem 0.65rem;
  border-radius: 20px;
  flex-shrink: 0;
  margin-top: 0.15rem;
}
.article-byline {
  font-family: 'Inter', sans-serif;
  font-size: 0.78rem;
  color: #888;
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 1rem;
  align-items: center;
}
.byline-cat {
  display: inline-block;
  padding: 0.15rem 0.55rem;
  border-radius: 3px;
  font-size: 0.72rem;
  font-weight: 600;
}
.article-summary {
  font-size: 1rem;
  line-height: 1.85;
  color: #2a2a2a;
  margin-bottom: 1.4rem;
}
.article-section-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #888;
  margin-bottom: 0.5rem;
}
.article-background {
  font-size: 0.92rem;
  line-height: 1.75;
  color: #555;
  background: #f7f7f3;
  border-left: 3px solid #d0d0c8;
  padding: 0.85rem 1rem;
  border-radius: 0 4px 4px 0;
  margin-bottom: 1.2rem;
}
.ref-links { margin-bottom: 1.2rem; }
.ref-links ul { list-style: none; padding: 0; margin: 0; }
.ref-links ul li {
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  color: #3b6fa0;
  padding: 0.2rem 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.ref-links ul li::before { content: '↗'; font-size: 0.75rem; opacity: 0.6; }
.tags-row { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag {
  font-family: 'Inter', sans-serif;
  font-size: 0.73rem;
  font-weight: 500;
  color: #555;
  background: #efefea;
  border: 1px solid #ddddd5;
  padding: 0.2rem 0.55rem;
  border-radius: 3px;
}

/* ── Category colors ── */
.cat-技术突破  { background: #e8f0fe; color: #1a56c4; }
.cat-产品发布  { background: #ede7f6; color: #5e35b1; }
.cat-商业资本  { background: #e8f5e9; color: #2e7d32; }
.cat-政策合规  { background: #fff3e0; color: #e65100; }

/* ── Deep dive cards ── */
.deep-dive-card {
  background: #fff;
  border: 1px solid #e0e0d8;
  border-radius: 8px;
  padding: 1.5rem 1.75rem;
  margin-bottom: 1.5rem;
}
.deep-dive-title {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin-bottom: 1rem;
  color: #0f172a;
}
.deep-dive-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #888;
  margin-bottom: 0.4rem;
  margin-top: 1rem;
}
.deep-dive-label:first-of-type { margin-top: 0; }
.deep-dive-text {
  font-size: 0.95rem;
  line-height: 1.8;
  color: #334155;
}
.findings-list {
  padding-left: 1.2rem;
  font-size: 0.95rem;
  line-height: 1.8;
  color: #334155;
}

/* ── Trend cards ── */
.trend-card {
  border-left: 3px solid #3b82f6;
  padding: 1.1rem 1.25rem;
  margin-bottom: 1.25rem;
  background: #f8faff;
  border-radius: 0 6px 6px 0;
}
.trend-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
  flex-wrap: wrap;
}
.trend-name {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}
.conf-badge {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}
.trend-desc {
  font-size: 0.95rem;
  line-height: 1.75;
  color: #475569;
  margin-bottom: 0.6rem;
}
.supporting-events {
  font-family: 'Inter', sans-serif;
  font-size: 0.78rem;
  color: #888;
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem 0.75rem;
}
.evt-ref::before { content: '· '; }

/* ── Risk / opportunity cards ── */
.risk-card {
  border-left: 3px solid #ef4444;
  padding: 1.1rem 1.25rem;
  margin-bottom: 1.25rem;
  background: #fff8f8;
  border-radius: 0 6px 6px 0;
}
.opp-card {
  border-left: 3px solid #10b981;
  padding: 1.1rem 1.25rem;
  margin-bottom: 1.25rem;
  background: #f0fdf4;
  border-radius: 0 6px 6px 0;
}
.risk-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}
.risk-type-badge {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}
.badge-risk  { background: #fee2e2; color: #b91c1c; }
.badge-opp   { background: #d1fae5; color: #065f46; }
.risk-title  { font-size: 1rem; font-weight: 700; color: #0f172a; }
.risk-desc {
  font-size: 0.95rem;
  line-height: 1.75;
  color: #475569;
  margin-bottom: 0.5rem;
}
.risk-related {
  font-family: 'Inter', sans-serif;
  font-size: 0.78rem;
  color: #888;
}

/* ── Executive summary block ── */
.summary-block {
  background: #f5f5f0;
  border: 1px solid #e0e0d8;
  border-radius: 6px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2.5rem;
}
.summary-block p {
  font-size: 0.97rem;
  line-height: 1.8;
  color: #334155;
}
.summary-block p + p { margin-top: 0.75rem; }
.summary-en {
  margin-top: 0.85rem;
  padding-top: 0.85rem;
  border-top: 1px solid #ddddd5;
  font-size: 0.9rem;
  color: #666;
  font-style: italic;
}

/* ── Footer ── */
.page-footer {
  margin-top: 4rem;
  padding-top: 1.5rem;
  border-top: 1px solid #d8d8d0;
  font-family: 'Inter', sans-serif;
  font-size: 0.78rem;
  color: #aaa;
  text-align: center;
}

/* ── Responsive ── */
@media (max-width: 640px) {
  .page-wrapper { padding: 1.5rem 1rem 4rem; }
  .report-title { font-size: 1.5rem; }
  .article-header { flex-direction: column; gap: 0.5rem; }
  .score-pill { align-self: flex-start; }
}
"""

# ── Category color helper ─────────────────────────────────────────────────────

_CAT_COLOR_CLASS = {
    "技术突破": "cat-技术突破",
    "产品发布": "cat-产品发布",
    "商业资本": "cat-商业资本",
    "政策合规": "cat-政策合规",
}
_CONF_COLORS = {
    "高": ("#dbeafe", "#1d4ed8"),
    "中": ("#fef3c7", "#b45309"),
    "低": ("#f3f4f6", "#6b7280"),
}


def _cat_class(cat: str) -> str:
    return _CAT_COLOR_CLASS.get(str(cat), "")


# ── Section 1: hot event article entry ───────────────────────────────────────

def _article_entry(ev: dict, scored_map: dict) -> str:
    rank     = ev.get("rank", 0)
    title    = _esc(ev.get("title", ""))
    score    = ev.get("impact_score", 0)
    cat      = str(ev.get("category", ""))
    summary  = _esc(ev.get("summary", ""))
    bg       = _esc(ev.get("background", ""))
    tags     = ev.get("tags", [])
    refs     = ev.get("reference_links", [])
    llm_url  = ev.get("source_url", "")

    sa = scored_map.get(llm_url, {})
    if not sa:
        sa = scored_map.get("__title__" + ev.get("title", ""), {})
    url = sa.get("original_url") or llm_url

    cat_class  = _cat_class(cat)
    title_html = (
        f'<a href="{_esc(url)}" target="_blank">{title}</a>' if url else title
    )

    source_name = sa.get("source_name", "")
    published   = str(sa.get("published_at", ""))[:10]
    byline_cat  = f'<span class="byline-cat {cat_class}">{_esc(cat)}</span>'
    extra = ""
    if source_name:
        extra += f" &nbsp;·&nbsp; <span>{_esc(source_name)}</span>"
    if published:
        extra += f" &nbsp;·&nbsp; <span>{_esc(published)}</span>"
    byline_html = byline_cat + extra

    bg_html = (
        f'<div class="article-section-label">背景</div>'
        f'<div class="article-background">{bg}</div>'
    ) if bg else ""

    refs_html = ""
    if refs:
        items = "".join(f"<li>{_esc(r)}</li>" for r in refs)
        refs_html = (
            f'<div class="ref-links">'
            f'<div class="article-section-label">参考资源</div>'
            f'<ul>{items}</ul></div>'
        )

    tags_html = ""
    if tags:
        spans = "".join(f'<span class="tag">{_esc(t)}</span>' for t in tags)
        tags_html = f'<div class="tags-row">{spans}</div>'

    return (
        f'<div class="article-entry" id="article-{rank}">'
        f'<div class="article-number">No. {rank}</div>'
        f'<div class="article-header">'
        f'<div class="article-title">{title_html}</div>'
        f'<div class="score-pill">{_score_stars(score)}</div>'
        f'</div>'
        f'<div class="article-byline">{byline_html}</div>'
        f'<p class="article-summary">{summary}</p>'
        f'{bg_html}{refs_html}{tags_html}'
        f'</div>'
    )


# ── Section 2: deep dives ─────────────────────────────────────────────────────

def _deep_dives_section(deep_dives: list[dict]) -> str:
    if not deep_dives:
        return ""
    cards = []
    for dd in deep_dives:
        title    = _esc(dd.get("title", ""))
        bg       = _esc(dd.get("background", ""))
        findings = dd.get("key_findings", [])
        tech_imp = _esc(dd.get("technical_impact", ""))
        biz_imp  = _esc(dd.get("business_impact", ""))
        outlook  = _esc(dd.get("outlook", ""))

        findings_html = "".join(f"<li>{_esc(f)}</li>" for f in findings)
        card = (
            f'<div class="deep-dive-card">'
            f'<div class="deep-dive-title">{title}</div>'
        )
        if bg:
            card += (
                f'<div class="deep-dive-label">事件背景</div>'
                f'<p class="deep-dive-text">{bg}</p>'
            )
        if findings:
            card += (
                f'<div class="deep-dive-label">关键发现</div>'
                f'<ul class="findings-list">{findings_html}</ul>'
            )
        if tech_imp:
            card += (
                f'<div class="deep-dive-label">技术影响</div>'
                f'<p class="deep-dive-text">{tech_imp}</p>'
            )
        if biz_imp:
            card += (
                f'<div class="deep-dive-label">商业影响</div>'
                f'<p class="deep-dive-text">{biz_imp}</p>'
            )
        if outlook:
            card += (
                f'<div class="deep-dive-label">未来展望</div>'
                f'<p class="deep-dive-text">{outlook}</p>'
            )
        card += '</div>'
        cards.append(card)

    return (
        f'<section id="section-deep-dive">'
        f'<h2 class="section-heading">'
        f'<span class="section-heading-icon">🔍</span>重要事件深度总结'
        f'</h2>'
        + "\n".join(cards)
        + '</section>'
    )


# ── Section 3: trend insights ─────────────────────────────────────────────────

def _trends_section(trend_insights: list[dict]) -> str:
    if not trend_insights:
        return ""
    cards = []
    for t in trend_insights:
        name   = _esc(t.get("trend_name", ""))
        desc   = _esc(t.get("description", ""))
        conf   = t.get("confidence", "中")
        evts   = t.get("supporting_events", [])

        bg_col, txt_col = _CONF_COLORS.get(conf, ("#f3f4f6", "#6b7280"))
        conf_badge = (
            f'<span class="conf-badge" style="background:{bg_col};color:{txt_col}">'
            f'置信度·{_esc(conf)}</span>'
        )
        evt_html = "".join(
            f'<span class="evt-ref">{_esc(e)}</span>' for e in evts
        )
        supporting = (
            f'<div class="supporting-events">{evt_html}</div>' if evt_html else ""
        )
        cards.append(
            f'<div class="trend-card">'
            f'<div class="trend-header"><span class="trend-name">{name}</span>{conf_badge}</div>'
            f'<p class="trend-desc">{desc}</p>'
            f'{supporting}'
            f'</div>'
        )

    return (
        f'<section id="section-trends">'
        f'<h2 class="section-heading">'
        f'<span class="section-heading-icon">📈</span>趋势判断'
        f'</h2>'
        + "\n".join(cards)
        + '</section>'
    )


# ── Section 4: risks and opportunities ───────────────────────────────────────

def _risks_section(risks_and_opportunities: list[dict]) -> str:
    if not risks_and_opportunities:
        return ""
    cards = []
    for r in risks_and_opportunities:
        is_risk = r.get("type", "risk") == "risk"
        card_cls   = "risk-card" if is_risk else "opp-card"
        badge_cls  = "badge-risk" if is_risk else "badge-opp"
        badge_text = "⚠ 风险" if is_risk else "✦ 机会"
        title = _esc(r.get("title", ""))
        desc  = _esc(r.get("description", ""))
        related = r.get("related_events", [])

        related_html = ""
        if related:
            items = "、".join(_esc(e) for e in related)
            related_html = f'<div class="risk-related">相关事件：{items}</div>'

        cards.append(
            f'<div class="{card_cls}">'
            f'<div class="risk-header">'
            f'<span class="risk-type-badge {badge_cls}">{badge_text}</span>'
            f'<span class="risk-title">{title}</span>'
            f'</div>'
            f'<p class="risk-desc">{desc}</p>'
            f'{related_html}'
            f'</div>'
        )

    return (
        f'<section id="section-risks">'
        f'<h2 class="section-heading">'
        f'<span class="section-heading-icon">⚡</span>风险或机会提示'
        f'</h2>'
        + "\n".join(cards)
        + '</section>'
    )


# ── TOC ───────────────────────────────────────────────────────────────────────

def _toc(events: list[dict], has_dives: bool, has_trends: bool, has_risks: bool) -> str:
    items = ""
    for ev in events:
        rank  = ev.get("rank", 0)
        title = _esc(ev.get("title", ""))
        score = ev.get("impact_score", 0)
        items += (
            f'<li><span class="toc-rank">{rank}.</span>'
            f'<a href="#article-{rank}">{title}</a>'
            f'<span class="toc-score">⭐ {score}.0</span></li>'
        )

    extra_links = ""
    if has_dives:
        extra_links += (
            '<li style="margin-top:0.5rem">'
            '<a href="#section-deep-dive" style="font-weight:600">🔍 重要事件深度总结</a></li>'
        )
    if has_trends:
        extra_links += (
            '<li><a href="#section-trends" style="font-weight:600">📈 趋势判断</a></li>'
        )
    if has_risks:
        extra_links += (
            '<li><a href="#section-risks" style="font-weight:600">⚡ 风险或机会提示</a></li>'
        )

    if not items and not extra_links:
        return ""

    return (
        f'<nav class="toc">'
        f'<div class="toc-title">本期内容</div>'
        f'<ul class="toc-list">{items}{extra_links}</ul>'
        f'</nav>'
    )


# ── Executive summary ────────────────────────────────────────────────────────

def _summary_block(zh: str, en: str) -> str:
    if not zh and not en:
        return ""
    inner = ""
    if zh:
        inner += f'<p>{_esc(zh)}</p>'
    if en:
        inner += f'<p class="summary-en">{_esc(en)}</p>'
    return f'<div class="summary-block">{inner}</div>'


# ── Main generator ────────────────────────────────────────────────────────────

def generate_html(report_date: str, report: dict, scored: list) -> str:
    """Return a complete self-contained HTML string for the given report."""
    scored_map: dict[str, dict] = {}
    for a in scored:
        orig_url = a.get("original_url", "")
        if orig_url:
            scored_map[orig_url] = a
        orig_title = a.get("original_title", "") or a.get("title", "")
        if orig_title:
            scored_map["__title__" + orig_title] = a

    events     = report.get("hot_events", [])
    deep_dives = report.get("deep_dives", [])
    trends     = report.get("trend_insights", [])
    risks      = report.get("risks_and_opportunities", [])
    total_p    = report.get("total_articles_processed", 0)
    total_f    = report.get("total_articles_after_filter", 0)
    gen_at     = str(report.get("generated_at", ""))[:16].replace("T", " ")
    n_events   = len(events)

    articles_html  = "\n".join(_article_entry(ev, scored_map) for ev in events)
    dive_html      = _deep_dives_section(deep_dives)
    trend_html     = _trends_section(trends)
    risk_html      = _risks_section(risks)
    toc_html       = _toc(events, bool(deep_dives), bool(trends), bool(risks))
    summary_html   = _summary_block(
        report.get("executive_summary_zh", ""),
        report.get("executive_summary_en", ""),
    )

    html = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>AI Insight Daily — {report_date}</title>\n'
        f"<style>{_CSS}</style>\n"
        "</head>\n<body>\n"
        '<div class="page-wrapper">\n\n'

        # ── Header
        '<header class="site-header">\n'
        '<div class="site-name">AI Insight Daily</div>\n'
        f'<h1 class="report-title">{report_date} 日报</h1>\n'
        '<p class="report-subtitle">AI 技术资讯精选日报 · AI-curated daily digest of tech and research news</p>\n'
        f'<div class="report-meta">共处理 {total_p} 条资讯，精选出 {n_events} 条重要内容</div>\n'
        '</header>\n\n'

        # ── TOC
        f'{toc_html}\n\n'

        # ── Executive summary
        f'{summary_html}\n\n'

        # ── Section 1: 今日热点
        f'<section id="section-hot-events">'
        f'<h2 class="section-heading">'
        f'<span class="section-heading-icon">🔥</span>今日 AI 领域主要热点'
        f'</h2>'
        f'{articles_html}'
        f'</section>\n\n'

        # ── Section 2: 深度总结
        f'{dive_html}\n\n'

        # ── Section 3: 趋势判断
        f'{trend_html}\n\n'

        # ── Section 4: 风险机会
        f'{risk_html}\n\n'

        # ── Footer
        '<footer class="page-footer">\n'
        f'生成时间：{gen_at} &nbsp;·&nbsp; 处理 {total_p} 条 &nbsp;·&nbsp; 筛选后 {total_f} 条\n'
        '</footer>\n\n'

        '</div>\n</body>\n</html>'
    )
    return html


def save_report_html(report_date: str, report: dict, scored: list) -> Path:
    html = generate_html(report_date, report, scored)
    out  = DATA_DIR / report_date / "report.html"
    out.write_text(html, encoding="utf-8")
    return out
