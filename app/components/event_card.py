"""Phase 9 -- Event card component for the Daily Report page."""

from __future__ import annotations

import streamlit as st

from app.components.score_badge import render_score_badge
from app.styles.theme import CATEGORY_COLORS, SENTIMENT_COLORS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CATEGORY_CSS_MAP: dict[str, str] = {
    "技术突破": "tech",
    "商业资本": "biz",
    "产品发布": "prod",
    "政策合规": "policy",
}


def _category_tag_html(category: str) -> str:
    css_cls = _CATEGORY_CSS_MAP.get(category, "tech")
    return f'<span class="category-tag {css_cls}">{category}</span>'


def _sentiment_html(sentiment: str) -> str:
    css_cls = sentiment.lower()  # Positive -> positive
    return f'<span class="sentiment-label {css_cls}">{sentiment}</span>'


def _entity_tags_html(entities: list[str]) -> str:
    if not entities:
        return ""
    tags = "".join(f'<span class="entity-tag">{e}</span>' for e in entities)
    return f'<div style="margin-top:6px;">{tags}</div>'


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_event_card(
    event: dict,
    rank: int,
    scored_articles: list[dict] | None = None,
) -> None:
    """Render a single event card with rank, category, score, summary, and
    optional detail button.

    Parameters
    ----------
    event : dict
        A hot_event dict from the daily report **or** a scored article dict.
        Expected keys: title, category, impact_score, summary.
        Optional keys from scored articles: core_entities,
        structured_analysis.sentiment_polarity, article_id.
    rank : int
        Display rank (1-based).
    scored_articles : list[dict] | None
        Full scored articles list; used to look up the matching article_id for
        the detail-page link.
    """
    title = event.get("title", "Untitled")
    category = event.get("category", "")
    score = event.get("impact_score", 0)
    summary = event.get("summary", "")

    # Try to resolve richer fields from scored articles
    article_id: str | None = event.get("article_id")
    matched_article: dict | None = None

    if scored_articles and not article_id:
        # Match by title (hot_event -> scored article)
        for sa in scored_articles:
            if sa.get("title") == title:
                matched_article = sa
                article_id = sa.get("article_id")
                break

    if matched_article is None and scored_articles and article_id:
        for sa in scored_articles:
            if sa.get("article_id") == article_id:
                matched_article = sa
                break

    # Entities
    entities: list[str] = []
    if matched_article:
        entities = matched_article.get("core_entities", [])
    elif "core_entities" in event:
        entities = event["core_entities"]

    # Sentiment
    sentiment: str = ""
    if matched_article:
        sa_analysis = matched_article.get("structured_analysis", {})
        if isinstance(sa_analysis, dict):
            sentiment = sa_analysis.get("sentiment_polarity", "")
    elif "structured_analysis" in event:
        sa_analysis = event.get("structured_analysis", {})
        if isinstance(sa_analysis, dict):
            sentiment = sa_analysis.get("sentiment_polarity", "")

    # Build HTML
    cat_html = _category_tag_html(category)
    score_html = render_score_badge(score)
    entity_html = _entity_tags_html(entities)
    sentiment_html = _sentiment_html(sentiment) if sentiment else ""

    card_html = f"""
    <div class="event-card">
        <div style="display:flex; align-items:flex-start; gap:12px;">
            <span class="event-rank">#{rank}</span>
            <div style="flex:1;">
                <div class="event-meta" style="margin-bottom:8px;">
                    {cat_html} {score_html} {sentiment_html}
                </div>
                <div class="event-title">{title}</div>
                <div class="event-summary">{summary}</div>
                {entity_html}
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Detail button
    if article_id:
        btn_key = f"detail_{article_id}_{rank}"
        if st.button("查看详情", key=btn_key):
            st.session_state["selected_article_id"] = article_id
            st.switch_page("pages/2_event_detail.py")
