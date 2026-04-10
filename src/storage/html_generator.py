"""HTML report generator — Horizon-style long-form digest page."""

import json
import html as html_lib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "output"


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return html_lib.escape(str(text or ""))


def _score_stars(score: int) -> str:
    """Format score as '⭐ 8.0/10'."""
    return f"⭐ {score}.0/10"


# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """\
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');

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

/* ── Header ── */
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
  margin-bottom: 0.75rem;
}
.toc-list {
  list-style: none;
  padding: 0;
}
.toc-list li {
  padding: 0.25rem 0;
  border-bottom: 1px solid #e8e8e2;
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}
.toc-list li:last-child { border-bottom: none; }
.toc-rank {
  font-family: 'Inter', sans-serif;
  font-size: 0.75rem;
  color: #aaa;
  min-width: 1.4rem;
}
.toc-list a {
  color: #1a1a1a;
  text-decoration: none;
  font-size: 0.92rem;
  line-height: 1.5;
}
.toc-list a:hover { text-decoration: underline; }
.toc-score {
  font-family: 'Inter', sans-serif;
  font-size: 0.72rem;
  color: #888;
  margin-left: auto;
  white-space: nowrap;
}

/* ── Article entries ── */
.article-entry {
  margin-bottom: 3.5rem;
  padding-bottom: 3rem;
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
  margin-bottom: 1rem;
}
.article-title {
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: -0.02em;
  flex: 1;
}
.article-title a {
  color: inherit;
  text-decoration: none;
}
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
  margin-bottom: 1.5rem;
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
  margin-bottom: 1.25rem;
}

.ref-links {
  margin-bottom: 1.25rem;
}
.ref-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.ref-links ul li {
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  color: #3b6fa0;
  padding: 0.2rem 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.ref-links ul li::before {
  content: '↗';
  font-size: 0.75rem;
  opacity: 0.6;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
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


def _cat_class(cat: str) -> str:
    return _CAT_COLOR_CLASS.get(str(cat), "")


# ── Article entry builder ─────────────────────────────────────────────────────

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

    # Resolve actual article URL
    sa = scored_map.get(llm_url, {})
    if not sa:
        sa = scored_map.get("__title__" + ev.get("title", ""), {})
    url = sa.get("original_url") or llm_url

    score_str = _score_stars(score)
    cat_class = _cat_class(cat)

    # Title — link if URL available
    title_html = (
        f'<a href="{_esc(url)}" target="_blank">{title}</a>' if url else title
    )

    # Byline
    source_name = sa.get("source_name", "")
    published   = str(sa.get("published_at", ""))[:10]
    byline_parts = []
    if source_name:
        byline_parts.append(f'<span>{_esc(source_name)}</span>')
    if published:
        byline_parts.append(f'<span>{_esc(published)}</span>')
    byline_cat = f'<span class="byline-cat {cat_class}">{_esc(cat)}</span>'
    byline_parts.insert(0, byline_cat)
    byline_html = " · ".join(byline_parts[1:]) if len(byline_parts) > 1 else ""
    byline_html = byline_cat + (" &nbsp;·&nbsp; " + byline_html if byline_html else "")

    # Background section
    bg_html = ""
    if bg:
        bg_html = (
            f'<div class="article-section-label">背景</div>'
            f'<div class="article-background">{bg}</div>'
        )

    # Reference links
    refs_html = ""
    if refs:
        items = "".join(f"<li>{_esc(r)}</li>" for r in refs)
        refs_html = (
            f'<div class="ref-links">'
            f'<div class="article-section-label">参考资源</div>'
            f'<ul>{items}</ul>'
            f'</div>'
        )

    # Tags
    tags_html = ""
    if tags:
        tag_spans = "".join(
            f'<span class="tag">{_esc(t)}</span>'
            for t in tags
        )
        tags_html = f'<div class="tags-row">{tag_spans}</div>'

    return (
        f'<div class="article-entry" id="article-{rank}">'
        f'<div class="article-number">No. {rank}</div>'
        f'<div class="article-header">'
        f'<div class="article-title">{title_html}</div>'
        f'<div class="score-pill">{score_str}</div>'
        f'</div>'
        f'<div class="article-byline">{byline_html}</div>'
        f'<p class="article-summary">{summary}</p>'
        f'{bg_html}'
        f'{refs_html}'
        f'{tags_html}'
        f'</div>'
    )


# ── TOC builder ───────────────────────────────────────────────────────────────

def _toc(events: list[dict]) -> str:
    if not events:
        return ""
    items = ""
    for ev in events:
        rank  = ev.get("rank", 0)
        title = _esc(ev.get("title", ""))
        score = ev.get("impact_score", 0)
        items += (
            f'<li>'
            f'<span class="toc-rank">{rank}.</span>'
            f'<a href="#article-{rank}">{title}</a>'
            f'<span class="toc-score">⭐ {score}.0</span>'
            f'</li>'
        )
    return (
        f'<nav class="toc">'
        f'<div class="toc-title">目录</div>'
        f'<ul class="toc-list">{items}</ul>'
        f'</nav>'
    )


# ── Main generator ────────────────────────────────────────────────────────────

def generate_html(report_date: str, report: dict, scored: list) -> str:
    """Return a complete self-contained HTML string for the given report."""
    # Build lookup map
    scored_map: dict[str, dict] = {}
    for a in scored:
        orig_url = a.get("original_url", "")
        if orig_url:
            scored_map[orig_url] = a
        orig_title = a.get("original_title", "") or a.get("title", "")
        if orig_title:
            scored_map["__title__" + orig_title] = a

    events    = report.get("hot_events", [])
    total_p   = report.get("total_articles_processed", 0)
    total_f   = report.get("total_articles_after_filter", 0)
    gen_at    = str(report.get("generated_at", ""))[:16].replace("T", " ")
    n_events  = len(events)

    toc_html      = _toc(events)
    articles_html = "\n".join(_article_entry(ev, scored_map) for ev in events)

    # Executive summary section
    zh = _esc(report.get("executive_summary_zh", ""))
    en = _esc(report.get("executive_summary_en", ""))
    summary_html = ""
    if zh or en:
        summary_html = (
            f'<div class="article-entry">'
            f'<div class="article-number">执行摘要</div>'
        )
        if zh:
            summary_html += f'<p class="article-summary">{zh}</p>'
        if en:
            summary_html += (
                f'<div class="article-section-label" style="margin-top:1rem">English Summary</div>'
                f'<p class="article-summary" style="color:#555;font-size:0.95rem">{en}</p>'
            )
        summary_html += '</div>'

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
        '<div class="page-wrapper">\n\n'

        # Header
        '<header class="site-header">\n'
        '<div class="site-name">AI Insight Daily</div>\n'
        f'<h1 class="report-title">{report_date} 日报</h1>\n'
        '<p class="report-subtitle">AI 技术资讯精选日报 · AI-curated daily digest of tech and research news</p>\n'
        f'<div class="report-meta">共处理 {total_p} 条资讯，精选出 {n_events} 条重要内容</div>\n'
        '</header>\n\n'

        # TOC
        f'{toc_html}\n\n'

        # Executive summary
        f'{summary_html}\n\n'

        # Articles
        f'{articles_html}\n\n'

        # Footer
        '<footer class="page-footer">\n'
        f'生成时间：{gen_at} &nbsp;·&nbsp; 处理 {total_p} 条 &nbsp;·&nbsp; 筛选后 {total_f} 条\n'
        '</footer>\n\n'

        '</div>\n'
        "</body>\n</html>"
    )
    return html


def save_report_html(report_date: str, report: dict, scored: list) -> Path:
    """Generate and write data/output/{report_date}/report.html, return path."""
    html = generate_html(report_date, report, scored)
    out  = DATA_DIR / report_date / "report.html"
    out.write_text(html, encoding="utf-8")
    return out
