"""Phase 9 -- Event Detail page.

Displays full details for a single scored article: structured analysis,
evaluation radar chart, score justifications, and link to the original source.
"""

import streamlit as st

from app.styles.theme import apply_theme, CATEGORY_COLORS
from app.components.score_badge import render_score_badge, get_score_color
from app.components.charts import create_radar_chart

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

apply_theme()

# ---------------------------------------------------------------------------
# Resolve the selected article
# ---------------------------------------------------------------------------

scored_articles: list[dict] = st.session_state.get("scored_articles", [])

# Try session state first, then query params
article_id: str | None = st.session_state.get("selected_article_id")
if article_id is None:
    params = st.query_params
    article_id = params.get("article_id")

if not article_id:
    st.info("No article selected. Go to the Daily Report page and click a detail button.")
    st.stop()

# Find the article
article: dict | None = None
for a in scored_articles:
    if a.get("article_id") == article_id:
        article = a
        break

if article is None:
    st.warning(f"Article '{article_id}' not found in loaded data.")
    st.stop()

# ---------------------------------------------------------------------------
# Header: title, category, score, source + date
# ---------------------------------------------------------------------------

title = article.get("title", "Untitled")
category = article.get("category", "")
impact_score = article.get("impact_score", 0)
final_score = article.get("final_score", 0.0)
source_name = article.get("source_name", "")
published_at = article.get("published_at", "")
original_url = article.get("original_url", "")
language = article.get("language", "")

# Category CSS class
_cat_css = {
    "技术突破": "tech",
    "商业资本": "biz",
    "产品发布": "prod",
    "政策合规": "policy",
}
cat_cls = _cat_css.get(category, "tech")
cat_html = f'<span class="category-tag {cat_cls}">{category}</span>'
score_html = render_score_badge(impact_score)

st.markdown(
    f'<div class="detail-header">'
    f'<div class="detail-title">{title}</div>'
    f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
    f'{cat_html} {score_html}'
    f'<span style="color:#4A5568;font-size:13px;">'
    f'{source_name} | {published_at} | {language.upper()}'
    f'</span>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Core entities
# ---------------------------------------------------------------------------

entities = article.get("core_entities", [])
if entities:
    tags_html = "".join(f'<span class="entity-tag">{e}</span>' for e in entities)
    st.markdown(f'<div style="margin-bottom:16px;">{tags_html}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Structured Analysis
# ---------------------------------------------------------------------------

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("#### Structured Analysis")

analysis = article.get("structured_analysis", {})
if isinstance(analysis, dict):
    sections = [
        ("BACKGROUND", analysis.get("background", "")),
        ("KEY ACTION", analysis.get("key_action", "")),
        ("TECHNICAL IMPLICATION", analysis.get("technical_implication", "")),
    ]
    for label, text in sections:
        if text:
            st.markdown(
                f'<div class="analysis-block">'
                f'<div class="analysis-label">{label}</div>'
                f'<div class="analysis-text">{text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Sentiment
    sentiment = analysis.get("sentiment_polarity", "")
    if sentiment:
        s_cls = sentiment.lower()
        st.markdown(
            f'<div style="margin-top:8px;">'
            f'Sentiment: <span class="sentiment-label {s_cls}">{sentiment}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Trend insight / Risk or opportunity (from article level)
# ---------------------------------------------------------------------------

trend_insight = article.get("trend_insight")
risk_or_opp = article.get("risk_or_opportunity")

if trend_insight or risk_or_opp:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    if trend_insight:
        st.markdown(
            f'<div class="analysis-block">'
            f'<div class="analysis-label">TREND INSIGHT</div>'
            f'<div class="analysis-text">{trend_insight}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if risk_or_opp:
        st.markdown(
            f'<div class="analysis-block" style="border-left-color:#D97706;">'
            f'<div class="analysis-label">RISK / OPPORTUNITY</div>'
            f'<div class="analysis-text">{risk_or_opp}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Evaluation — Radar chart + justifications table
# ---------------------------------------------------------------------------

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("#### Evaluation")

evaluation = article.get("evaluation", {})
if isinstance(evaluation, dict) and evaluation:
    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        fig = create_radar_chart(evaluation)
        st.plotly_chart(fig, use_container_width=False, config={"displayModeBar": False})

    with col_table:
        dim_rows = [
            ("技术新颖性", "technical_novelty"),
            ("影响力", "potential_impact"),
            ("成熟度", "readiness_level"),
        ]
        table_html = (
            '<table style="width:100%;border-collapse:collapse;font-size:14px;">'
            '<thead><tr style="border-bottom:2px solid #E2E8F0;">'
            '<th style="text-align:left;padding:8px;">Dimension</th>'
            '<th style="text-align:center;padding:8px;">Score</th>'
            '<th style="text-align:left;padding:8px;">Justification</th>'
            '</tr></thead><tbody>'
        )

        for label, key in dim_rows:
            dim = evaluation.get(key, {})
            if isinstance(dim, dict):
                s = dim.get("score", 0)
                just = dim.get("justification", "")
                color = get_score_color(s * 2)  # map 1-5 to approximate 1-10 scale
                table_html += (
                    f'<tr style="border-bottom:1px solid #E2E8F0;">'
                    f'<td style="padding:8px;">{label}</td>'
                    f'<td style="text-align:center;padding:8px;">'
                    f'<span style="font-weight:700;color:{color};">{s}/5</span></td>'
                    f'<td style="padding:8px;color:#4A5568;">{just}</td>'
                    f'</tr>'
                )

        # Additional info: target_domain from potential_impact
        potential_impact = evaluation.get("potential_impact", {})
        if isinstance(potential_impact, dict):
            domain = potential_impact.get("target_domain", "")
            if domain:
                table_html += (
                    f'<tr style="border-bottom:1px solid #E2E8F0;">'
                    f'<td style="padding:8px;" colspan="3">'
                    f'<span style="color:#4A5568;font-size:12px;">Target domain: {domain}</span>'
                    f'</td></tr>'
                )

        table_html += '</tbody></table>'
        st.markdown(table_html, unsafe_allow_html=True)

    # Critical risks from evaluation
    critical_risks = evaluation.get("critical_risks", [])
    if critical_risks:
        st.markdown("**Critical Risks:**")
        for risk in critical_risks:
            st.markdown(f"- {risk}")

# ---------------------------------------------------------------------------
# Final scores summary
# ---------------------------------------------------------------------------

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.metric("Impact Score", f"{impact_score}/10")
with col_s2:
    st.metric("Final Score", f"{final_score:.1f}")
with col_s3:
    st.metric("Source Weight", f"{article.get('source_weight', 1.0):.1f}")

# ---------------------------------------------------------------------------
# Link to original article
# ---------------------------------------------------------------------------

if original_url:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    original_title = article.get("original_title", "Original Article")
    st.markdown(
        f'<a href="{original_url}" target="_blank" '
        f'style="color:#2563EB;text-decoration:none;font-weight:500;">'
        f'Read original: {original_title}</a>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Back button
# ---------------------------------------------------------------------------

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
if st.button("Back to Daily Report"):
    st.switch_page("pages/1_daily_report.py")
