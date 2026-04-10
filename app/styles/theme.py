"""Phase 9 -- Dashboard Theme: Bloomberg/Newsroom style constants and CSS."""

import streamlit as st


# ---------------------------------------------------------------------------
# Color palettes
# ---------------------------------------------------------------------------

CATEGORY_COLORS: dict[str, str] = {
    "技术突破": "#2563EB",
    "商业资本": "#059669",
    "产品发布": "#7C3AED",
    "政策合规": "#D97706",
}

SCORE_COLORS: dict[str, str] = {
    "high": "#059669",   # 8-10
    "mid": "#D97706",    # 5-7
    "low": "#DC2626",    # 1-4
}

SENTIMENT_COLORS: dict[str, str] = {
    "Positive": "#059669",
    "Neutral": "#6C757D",
    "Negative": "#DC2626",
}

CHART_COLORS: dict[str, str] = {
    "primary": "#2563EB",
    "secondary": "#059669",
    "accent": "#7C3AED",
    "warning": "#D97706",
    "danger": "#DC2626",
    "muted": "#6C757D",
    "bg": "#FFFFFF",
    "card_bg": "#F8F9FA",
    "sidebar_bg": "#1A1A2E",
    "text_primary": "#1A1A2E",
    "text_secondary": "#4A5568",
    "border": "#E2E8F0",
}

PLOTLY_LAYOUT: dict = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {
        "family": '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif',
        "color": "#1A1A2E",
        "size": 13,
    },
    "margin": {"l": 40, "r": 40, "t": 40, "b": 40},
    "hoverlabel": {
        "bgcolor": "#FFFFFF",
        "bordercolor": "#E2E8F0",
        "font_size": 12,
    },
}


# ---------------------------------------------------------------------------
# Full custom CSS
# ---------------------------------------------------------------------------

CUSTOM_CSS: str = """
<style>
/* ---- Base font ---- */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
    color: #1A1A2E;
}

/* ---- Hide Streamlit default colored top bar ---- */
header[data-testid="stHeader"] {
    background: #FFFFFF !important;
    border-bottom: 1px solid #E2E8F0;
}
div[data-testid="stDecoration"] {
    display: none !important;
}

/* ---- Reduce default spacing ---- */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
    max-width: 1200px;
}

/* ---- Sidebar styling ---- */
section[data-testid="stSidebar"] > div:first-child {
    background-color: #1A1A2E;
    color: #E2E8F0;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #E2E8F0 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label {
    color: #A0AEC0 !important;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ---- Metric card styling ---- */
div[data-testid="stMetric"] {
    background: #F8F9FA;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 16px 20px;
}
div[data-testid="stMetric"] label {
    color: #4A5568 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #1A1A2E !important;
}

/* ---- Event card ---- */
.event-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: box-shadow 0.15s ease;
}
.event-card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.event-card .event-rank {
    font-size: 14px;
    font-weight: 700;
    color: #4A5568;
    margin-right: 8px;
}
.event-card .event-title {
    font-size: 16px;
    font-weight: 600;
    color: #1A1A2E;
    margin-bottom: 8px;
    line-height: 1.4;
}
.event-card .event-summary {
    font-size: 14px;
    color: #4A5568;
    line-height: 1.6;
    margin-bottom: 10px;
}
.event-card .event-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

/* ---- Category tag ---- */
.category-tag {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 4px;
    color: #FFFFFF;
    letter-spacing: 0.02em;
}
.category-tag.tech { background: #2563EB; }
.category-tag.biz  { background: #059669; }
.category-tag.prod { background: #7C3AED; }
.category-tag.policy { background: #D97706; }

/* ---- Score badge ---- */
.score-badge {
    display: inline-block;
    font-size: 13px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    color: #FFFFFF;
    min-width: 32px;
    text-align: center;
}
.score-badge.high { background: #059669; }
.score-badge.mid  { background: #D97706; }
.score-badge.low  { background: #DC2626; }

/* ---- Sentiment label ---- */
.sentiment-label {
    display: inline-block;
    font-size: 12px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid;
}
.sentiment-label.positive { color: #059669; border-color: #059669; background: rgba(5,150,105,0.08); }
.sentiment-label.neutral  { color: #6C757D; border-color: #6C757D; background: rgba(108,117,125,0.08); }
.sentiment-label.negative { color: #DC2626; border-color: #DC2626; background: rgba(220,38,38,0.08); }

/* ---- Entity tag ---- */
.entity-tag {
    display: inline-block;
    font-size: 12px;
    color: #2563EB;
    background: rgba(37,99,235,0.08);
    border: 1px solid rgba(37,99,235,0.2);
    padding: 1px 8px;
    border-radius: 4px;
    margin-right: 4px;
    margin-bottom: 4px;
}

/* ---- Section divider ---- */
.section-divider {
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 24px 0 16px 0;
}

/* ---- Detail page header ---- */
.detail-header {
    margin-bottom: 24px;
}
.detail-header .detail-title {
    font-size: 22px;
    font-weight: 700;
    color: #1A1A2E;
    margin-bottom: 12px;
    line-height: 1.3;
}

/* ---- Analysis block ---- */
.analysis-block {
    background: #F8F9FA;
    border-left: 3px solid #2563EB;
    padding: 14px 18px;
    margin-bottom: 12px;
    border-radius: 0 6px 6px 0;
}
.analysis-block .analysis-label {
    font-size: 12px;
    font-weight: 600;
    color: #4A5568;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}
.analysis-block .analysis-text {
    font-size: 14px;
    color: #1A1A2E;
    line-height: 1.6;
}

/* ---- Score dots (kept for optional use) ---- */
.score-dots {
    display: inline-flex;
    gap: 3px;
}
.score-dots .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #E2E8F0;
}
.score-dots .dot.filled { background: #2563EB; }
</style>
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_theme() -> None:
    """Inject the custom CSS into the Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
