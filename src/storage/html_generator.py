"""HTML report generator — tab-based Horizon-style digest page.

Four tabs:
  Tab 1 — 今日热点        hot_events
  Tab 2 — 深度总结        deep_dives
  Tab 3 — 趋势判断        trend_insights
  Tab 4 — 风险与机会       risks_and_opportunities
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
  background: #f8f8f6;
  color: #1a1a1a;
  line-height: 1.8;
  font-size: 16px;
  min-height: 100vh;
}

/* ── App shell ── */
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ── Site header ── */
.site-header {
  background: #1a1a1a;
  color: #fff;
  padding: 1.1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 200;
  box-shadow: 0 2px 8px rgba(0,0,0,.25);
}
.header-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.brand-logo {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.brand-name {
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.brand-sub {
  font-family: 'Inter', sans-serif;
  font-size: 0.68rem;
  color: #94a3b8;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-top: 0.1rem;
}
.header-meta {
  text-align: right;
}
.date-chip {
  font-family: 'Inter', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: #fcd34d;
  letter-spacing: 0.04em;
}
.stat-line {
  font-family: 'Inter', sans-serif;
  font-size: 0.68rem;
  color: #64748b;
  margin-top: 0.2rem;
}

/* ── Tab bar ── */
.tab-bar {
  background: #fff;
  border-bottom: 1px solid #e5e5e0;
  position: sticky;
  top: 60px;
  z-index: 100;
  display: flex;
  padding: 0 2rem;
  box-shadow: 0 1px 4px rgba(0,0,0,.04);
  overflow-x: auto;
  scrollbar-width: none;
}
.tab-bar::-webkit-scrollbar { display: none; }

.tab-btn {
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  padding: 0.95rem 1.2rem;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.15s, border-color 0.15s;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.tab-btn:hover { color: #1a1a1a; }
.tab-btn.active {
  color: #1a1a1a;
  border-bottom-color: #1a1a1a;
}
.tab-count {
  font-size: 0.68rem;
  font-weight: 700;
  background: #f0f0ec;
  color: #888;
  padding: 0.1rem 0.45rem;
  border-radius: 10px;
}
.tab-btn.active .tab-count {
  background: #1a1a1a;
  color: #fff;
}

/* ── Content panels ── */
.tab-panel {
  display: none;
  max-width: 780px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 5rem;
  width: 100%;
}
.tab-panel.active { display: block; }

/* ── Executive summary (shown on hot-events tab) ── */
.summary-block {
  background: #fff;
  border: 1px solid #e5e5e0;
  border-radius: 8px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 2.5rem;
}
.summary-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #aaa;
  margin-bottom: 0.6rem;
}
.summary-block p {
  font-size: 0.97rem;
  line-height: 1.8;
  color: #334155;
}
.summary-en {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #eee;
  font-size: 0.9rem;
  color: #888;
  font-style: italic;
}

/* ── Hot event article entry ── */
.article-entry {
  margin-bottom: 2.75rem;
  padding-bottom: 2.5rem;
  border-bottom: 1px solid #e0e0d8;
}
.article-entry:last-child { border-bottom: none; }

.article-number {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #bbb;
  margin-bottom: 0.4rem;
}
.article-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.8rem;
}
.article-title {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: -0.02em;
  flex: 1;
}
.article-title a { color: inherit; text-decoration: none; }
.article-title a:hover { text-decoration: underline; }
.score-pill {
  font-family: 'Inter', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
  background: #fff8e6;
  border: 1px solid #f0d070;
  color: #7a5c00;
  padding: 0.28rem 0.6rem;
  border-radius: 20px;
  flex-shrink: 0;
  margin-top: 0.15rem;
}
.article-byline {
  font-family: 'Inter', sans-serif;
  font-size: 0.76rem;
  color: #999;
  margin-bottom: 0.95rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem 0.8rem;
  align-items: center;
}
.byline-cat {
  display: inline-block;
  padding: 0.12rem 0.5rem;
  border-radius: 3px;
  font-size: 0.7rem;
  font-weight: 700;
}
.article-summary {
  font-size: 0.98rem;
  line-height: 1.85;
  color: #2a2a2a;
  margin-bottom: 1.3rem;
}
.field-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #aaa;
  margin-bottom: 0.45rem;
}
.article-background {
  font-size: 0.9rem;
  line-height: 1.75;
  color: #555;
  background: #f7f7f3;
  border-left: 3px solid #d0d0c8;
  padding: 0.8rem 1rem;
  border-radius: 0 4px 4px 0;
  margin-bottom: 1.1rem;
}
.ref-links { margin-bottom: 1.1rem; }
.ref-links ul { list-style: none; padding: 0; margin: 0; }
.ref-links ul li {
  font-family: 'Inter', sans-serif;
  font-size: 0.83rem;
  color: #3b6fa0;
  padding: 0.18rem 0;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.ref-links ul li::before { content: '↗'; font-size: 0.72rem; opacity: 0.55; }
.tags-row { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.tag {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  font-weight: 500;
  color: #666;
  background: #efefea;
  border: 1px solid #ddddd5;
  padding: 0.18rem 0.5rem;
  border-radius: 3px;
}

/* ── Category colors ── */
.cat-技术突破 { background: #e8f0fe; color: #1a56c4; }
.cat-产品发布 { background: #ede7f6; color: #5e35b1; }
.cat-商业资本 { background: #e8f5e9; color: #2e7d32; }
.cat-政策合规 { background: #fff3e0; color: #e65100; }

/* ── Panel heading ── */
.panel-heading {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #aaa;
  margin-bottom: 1.5rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid #e5e5e0;
}

/* ── Deep dive cards ── */
.deep-dive-card {
  background: #fff;
  border: 1px solid #e5e5e0;
  border-radius: 8px;
  padding: 1.5rem 1.75rem;
  margin-bottom: 1.5rem;
}
.deep-dive-title {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin-bottom: 1.1rem;
  color: #0f172a;
  line-height: 1.4;
}
.dive-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #aaa;
  margin-bottom: 0.4rem;
  margin-top: 1rem;
}
.dive-label:first-of-type { margin-top: 0; }
.dive-text {
  font-size: 0.95rem;
  line-height: 1.8;
  color: #334155;
}
.findings-list {
  padding-left: 1.25rem;
  font-size: 0.95rem;
  line-height: 1.8;
  color: #334155;
}
.empty-tip {
  font-family: 'Inter', sans-serif;
  font-size: 0.9rem;
  color: #bbb;
  text-align: center;
  padding: 3rem 0;
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
  margin-bottom: 0.55rem;
  flex-wrap: wrap;
}
.trend-name {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}
.conf-badge {
  font-family: 'Inter', sans-serif;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.18rem 0.55rem;
  border-radius: 4px;
}
.trend-desc {
  font-size: 0.95rem;
  line-height: 1.75;
  color: #475569;
  margin-bottom: 0.55rem;
}
.supporting-events {
  font-family: 'Inter', sans-serif;
  font-size: 0.76rem;
  color: #aaa;
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.6rem;
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
.risk-badge {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.18rem 0.55rem;
  border-radius: 4px;
}
.badge-risk { background: #fee2e2; color: #b91c1c; }
.badge-opp  { background: #d1fae5; color: #065f46; }
.risk-title { font-size: 1rem; font-weight: 700; color: #0f172a; }
.risk-desc  {
  font-size: 0.95rem;
  line-height: 1.75;
  color: #475569;
  margin-bottom: 0.5rem;
}
.risk-related {
  font-family: 'Inter', sans-serif;
  font-size: 0.76rem;
  color: #aaa;
}

/* ── Footer ── */
.page-footer {
  background: #fff;
  border-top: 1px solid #e5e5e0;
  font-family: 'Inter', sans-serif;
  font-size: 0.75rem;
  color: #ccc;
  text-align: center;
  padding: 1.25rem;
}

/* ── Responsive ── */
@media (max-width: 640px) {
  .site-header { padding: 1rem 1rem; }
  .tab-bar { padding: 0 0.5rem; }
  .tab-btn { padding: 0.8rem 0.8rem; font-size: 0.8rem; }
  .tab-panel { padding: 1.5rem 1rem 4rem; }
  .article-header { flex-direction: column; gap: 0.4rem; }
  .score-pill { align-self: flex-start; }
}
"""

# ── JS ────────────────────────────────────────────────────────────────────────

_JS = """\
function switchTab(id) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + id).classList.add('active');
  document.getElementById('tab-' + id).classList.add('active');
  history.replaceState(null, '', '#' + id);
}
// Restore tab from URL hash
(function() {
  var hash = location.hash.replace('#', '');
  var valid = ['hot', 'deep', 'trends', 'risks'];
  if (valid.indexOf(hash) !== -1) switchTab(hash);
})();
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


# ── Tab 1: hot event article entry ────────────────────────────────────────────

def _article_entry(ev: dict, scored_map: dict) -> str:
    rank    = ev.get("rank", 0)
    title   = _esc(ev.get("title", ""))
    score   = ev.get("impact_score", 0)
    cat     = str(ev.get("category", ""))
    summary = _esc(ev.get("summary", ""))
    bg      = _esc(ev.get("background", ""))
    tags    = ev.get("tags", [])
    refs    = ev.get("reference_links", [])
    llm_url = ev.get("source_url", "")

    sa = scored_map.get(llm_url, {})
    if not sa:
        sa = scored_map.get("__title__" + ev.get("title", ""), {})
    url = sa.get("original_url") or llm_url

    cat_class  = _cat_class(cat)
    title_html = (
        f'<a href="{_esc(url)}" target="_blank">{title}</a>' if url else title
    )
    byline_cat = f'<span class="byline-cat {cat_class}">{_esc(cat)}</span>'
    extra = ""
    if sa.get("source_name"):
        extra += f" &nbsp;·&nbsp; {_esc(sa['source_name'])}"
    if str(sa.get("published_at", ""))[:10]:
        extra += f" &nbsp;·&nbsp; {str(sa['published_at'])[:10]}"

    bg_html = (
        f'<div class="field-label">背景</div>'
        f'<div class="article-background">{bg}</div>'
    ) if bg else ""

    refs_html = ""
    if refs:
        items = "".join(f"<li>{_esc(r)}</li>" for r in refs)
        refs_html = (
            f'<div class="ref-links">'
            f'<div class="field-label">参考资源</div>'
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
        f'<div class="article-byline">{byline_cat}{extra}</div>'
        f'<p class="article-summary">{summary}</p>'
        f'{bg_html}{refs_html}{tags_html}'
        f'</div>'
    )


# ── Tab 2: deep dives ─────────────────────────────────────────────────────────

def _deep_dives_panel(deep_dives: list[dict]) -> str:
    if not deep_dives:
        return '<p class="empty-tip">本期暂无深度分析内容</p>'
    cards = []
    for dd in deep_dives:
        card = f'<div class="deep-dive-card"><div class="deep-dive-title">{_esc(dd.get("title",""))}</div>'
        if dd.get("background"):
            card += f'<div class="dive-label">事件背景</div><p class="dive-text">{_esc(dd["background"])}</p>'
        if dd.get("key_findings"):
            items = "".join(f"<li>{_esc(f)}</li>" for f in dd["key_findings"])
            card += f'<div class="dive-label">关键发现</div><ul class="findings-list">{items}</ul>'
        if dd.get("technical_impact"):
            card += f'<div class="dive-label">技术影响</div><p class="dive-text">{_esc(dd["technical_impact"])}</p>'
        if dd.get("business_impact"):
            card += f'<div class="dive-label">商业影响</div><p class="dive-text">{_esc(dd["business_impact"])}</p>'
        if dd.get("outlook"):
            card += f'<div class="dive-label">未来展望</div><p class="dive-text">{_esc(dd["outlook"])}</p>'
        card += '</div>'
        cards.append(card)
    return "\n".join(cards)


# ── Tab 3: trends ─────────────────────────────────────────────────────────────

def _trends_panel(trends: list[dict]) -> str:
    if not trends:
        return '<p class="empty-tip">本期暂无趋势分析内容</p>'
    cards = []
    for t in trends:
        conf = t.get("confidence", "中")
        bg_col, txt_col = _CONF_COLORS.get(conf, ("#f3f4f6", "#6b7280"))
        badge = (
            f'<span class="conf-badge" style="background:{bg_col};color:{txt_col}">'
            f'置信度·{_esc(conf)}</span>'
        )
        evts = "".join(
            f'<span class="evt-ref">{_esc(e)}</span>'
            for e in t.get("supporting_events", [])
        )
        supporting = f'<div class="supporting-events">{evts}</div>' if evts else ""
        cards.append(
            f'<div class="trend-card">'
            f'<div class="trend-header"><span class="trend-name">{_esc(t.get("trend_name",""))}</span>{badge}</div>'
            f'<p class="trend-desc">{_esc(t.get("description",""))}</p>'
            f'{supporting}'
            f'</div>'
        )
    return "\n".join(cards)


# ── Tab 4: risks and opportunities ───────────────────────────────────────────

def _risks_panel(risks: list[dict]) -> str:
    if not risks:
        return '<p class="empty-tip">本期暂无风险或机会提示</p>'
    cards = []
    for r in risks:
        is_risk   = r.get("type", "risk") == "risk"
        card_cls  = "risk-card" if is_risk else "opp-card"
        badge_cls = "badge-risk" if is_risk else "badge-opp"
        badge_txt = "⚠ 风险" if is_risk else "✦ 机会"
        related   = r.get("related_events", [])
        related_html = (
            f'<div class="risk-related">相关事件：{"、".join(_esc(e) for e in related)}</div>'
        ) if related else ""
        cards.append(
            f'<div class="{card_cls}">'
            f'<div class="risk-header">'
            f'<span class="risk-badge {badge_cls}">{badge_txt}</span>'
            f'<span class="risk-title">{_esc(r.get("title",""))}</span>'
            f'</div>'
            f'<p class="risk-desc">{_esc(r.get("description",""))}</p>'
            f'{related_html}'
            f'</div>'
        )
    return "\n".join(cards)


# ── Main generator ────────────────────────────────────────────────────────────

def generate_html(report_date: str, report: dict, scored: list) -> str:
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
    n_dives    = len(deep_dives)
    n_trends   = len(trends)
    n_risks    = len(risks)

    # Build tab badge HTML (show count only when > 0)
    def _badge(n: int) -> str:
        return f'<span class="tab-count">{n}</span>' if n else ""

    # Executive summary
    zh = _esc(report.get("executive_summary_zh", ""))
    en = _esc(report.get("executive_summary_en", ""))
    summary_html = ""
    if zh or en:
        inner = ""
        if zh:
            inner += f'<p>{zh}</p>'
        if en:
            inner += f'<p class="summary-en">{en}</p>'
        summary_html = (
            f'<div class="summary-block">'
            f'<div class="summary-label">执行摘要</div>'
            f'{inner}'
            f'</div>'
        )

    articles_html = "\n".join(_article_entry(ev, scored_map) for ev in events)

    html = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>AI Insight Daily — {report_date}</title>\n'
        f"<style>{_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        '<div class="app-shell">\n\n'

        # ── Header
        '<header class="site-header">\n'
        '  <div class="header-brand">\n'
        '    <div class="brand-logo">⚡</div>\n'
        '    <div>\n'
        '      <div class="brand-name">AI Insight Daily</div>\n'
        '      <div class="brand-sub">AI-curated daily digest</div>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="header-meta">\n'
        f'    <div class="date-chip">📅 {report_date}</div>\n'
        f'    <div class="stat-line">处理 {total_p} 条 · 精选 {n_events} 条 · {gen_at}</div>\n'
        '  </div>\n'
        '</header>\n\n'

        # ── Tab bar
        '<nav class="tab-bar">\n'
        f'  <button class="tab-btn active" id="tab-hot" onclick="switchTab(\'hot\')">'
        f'🔥 今日热点{_badge(n_events)}</button>\n'
        f'  <button class="tab-btn" id="tab-deep" onclick="switchTab(\'deep\')">'
        f'🔍 深度总结{_badge(n_dives)}</button>\n'
        f'  <button class="tab-btn" id="tab-trends" onclick="switchTab(\'trends\')">'
        f'📈 趋势判断{_badge(n_trends)}</button>\n'
        f'  <button class="tab-btn" id="tab-risks" onclick="switchTab(\'risks\')">'
        f'⚡ 风险与机会{_badge(n_risks)}</button>\n'
        '</nav>\n\n'

        # ── Tab 1: 今日热点
        '<div class="tab-panel active" id="panel-hot">\n'
        f'  {summary_html}\n'
        f'  {articles_html}\n'
        '</div>\n\n'

        # ── Tab 2: 深度总结
        '<div class="tab-panel" id="panel-deep">\n'
        f'  <div class="panel-heading">重要事件深度总结</div>\n'
        f'  {_deep_dives_panel(deep_dives)}\n'
        '</div>\n\n'

        # ── Tab 3: 趋势判断
        '<div class="tab-panel" id="panel-trends">\n'
        f'  <div class="panel-heading">趋势判断 · 技术 / 应用 / 政策 / 资本</div>\n'
        f'  {_trends_panel(trends)}\n'
        '</div>\n\n'

        # ── Tab 4: 风险与机会
        '<div class="tab-panel" id="panel-risks">\n'
        f'  <div class="panel-heading">风险或机会提示</div>\n'
        f'  {_risks_panel(risks)}\n'
        '</div>\n\n'

        # ── Footer
        f'<footer class="page-footer">'
        f'生成时间：{gen_at} &nbsp;·&nbsp; 处理 {total_p} 条 &nbsp;·&nbsp; 筛选后 {total_f} 条'
        f'</footer>\n\n'

        '</div>\n'
        f'<script>{_JS}</script>\n'
        '</body>\n</html>'
    )
    return html


def save_report_html(
    report_date: str,
    report: dict,
    scored: list,
    out_dir: Path | None = None,
) -> Path:
    """生成并保存日报 HTML。

    Parameters
    ----------
    out_dir : Path | None
        自定义输出目录；为 None 时使用 DATA_DIR / report_date。
        多日汇总模式传入 summary_{start}_{end}/ 目录。
    """
    html = generate_html(report_date, report, scored)
    if out_dir is None:
        out_dir = DATA_DIR / report_date
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "report.html"
    out.write_text(html, encoding="utf-8")
    return out
