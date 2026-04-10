"""Phase 9 -- Daily Report page.

Displays the executive summary, metric cards, hot events, trend insights,
and risks & opportunities from the loaded daily report.
"""

import streamlit as st

from app.styles.theme import apply_theme
from app.components.event_card import render_event_card
from app.components.score_badge import render_score_badge

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

apply_theme()

# ---------------------------------------------------------------------------
# Load data from session state
# ---------------------------------------------------------------------------

report: dict | None = st.session_state.get("report")
scored_articles: list[dict] = st.session_state.get("scored_articles", [])
filtered_articles: list[dict] = st.session_state.get("filtered_articles", [])
selected_date: str = st.session_state.get("selected_date", "")

if report is None:
    st.warning("No report loaded. Please select a date from the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------

st.markdown(f"## Daily Report  /  {report.get('report_date', '')}")

# ---------------------------------------------------------------------------
# Executive Summary
# ---------------------------------------------------------------------------

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

summary_zh = report.get("executive_summary_zh", "")
summary_en = report.get("executive_summary_en", "")

if summary_zh or summary_en:
    st.markdown("#### Executive Summary")

    lang_choice = st.radio(
        "Language",
        options=["中文", "English"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    if lang_choice == "中文" and summary_zh:
        st.markdown(
            f'<div class="analysis-block">'
            f'<div class="analysis-text">{summary_zh}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    elif lang_choice == "English" and summary_en:
        st.markdown(
            f'<div class="analysis-block">'
            f'<div class="analysis-text">{summary_en}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Summary not available in the selected language.")

# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

total_articles = report.get("total_articles_after_filter", 0)
hot_events = report.get("hot_events", [])
trend_insights = report.get("trend_insights", [])

# Compute high-score count (impact_score >= 8)
high_score_count = sum(
    1 for e in hot_events if e.get("impact_score", 0) >= 8
)

# Average score across hot events
avg_score = 0.0
if hot_events:
    avg_score = round(
        sum(e.get("impact_score", 0) for e in hot_events) / len(hot_events),
        1,
    )

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Articles", total_articles)
with col2:
    st.metric("High-Score Events", high_score_count)
with col3:
    st.metric("Avg. Impact Score", avg_score)
with col4:
    st.metric("Trend Insights", len(trend_insights))

# ---------------------------------------------------------------------------
# Hot Events
# ---------------------------------------------------------------------------

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("#### Hot Events")

if not hot_events:
    st.info("No hot events in this report.")
else:
    # Apply category + score filters from sidebar to hot events
    selected_categories = st.session_state.get("selected_categories", [])
    min_score = st.session_state.get("min_score", 1)

    for event in hot_events:
        cat = event.get("category", "")
        score = event.get("impact_score", 0)

        if selected_categories and cat not in selected_categories:
            continue
        if score < min_score:
            continue

        render_event_card(
            event=event,
            rank=event.get("rank", 0),
            scored_articles=scored_articles,
        )

# ---------------------------------------------------------------------------
# Trend Insights
# ---------------------------------------------------------------------------

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("#### Trend Insights")

if not trend_insights:
    st.info("No trend insights in this report.")
else:
    for trend in trend_insights:
        trend_name = trend.get("trend_name", "Untitled Trend")
        confidence = trend.get("confidence", "")
        description = trend.get("description", "")
        supporting = trend.get("supporting_events", [])

        with st.expander(f"{trend_name}  [{confidence}]", expanded=False):
            st.markdown(description)
            if supporting:
                st.markdown("**Supporting events:**")
                for evt_title in supporting:
                    st.markdown(f"- {evt_title}")

# ---------------------------------------------------------------------------
# Risks & Opportunities
# ---------------------------------------------------------------------------

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("#### Risks & Opportunities")

risks_opps = report.get("risks_and_opportunities", [])
if not risks_opps:
    st.info("No risks or opportunities identified in this report.")
else:
    for item in risks_opps:
        item_type = item.get("type", "risk")
        title = item.get("title", "")
        description = item.get("description", "")
        related = item.get("related_events", [])

        type_label = "RISK" if item_type == "risk" else "OPPORTUNITY"
        type_color = "#DC2626" if item_type == "risk" else "#059669"

        st.markdown(
            f'<div class="event-card">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
            f'<span style="font-size:12px;font-weight:700;color:{type_color};'
            f'text-transform:uppercase;letter-spacing:0.05em;">{type_label}</span>'
            f'</div>'
            f'<div class="event-title">{title}</div>'
            f'<div class="event-summary">{description}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if related:
            with st.expander("Related events", expanded=False):
                for r in related:
                    st.markdown(f"- {r}")
