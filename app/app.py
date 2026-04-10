"""Phase 9 -- AI Insight Daily: Main Streamlit entry point.

Run with:
    streamlit run app/app.py
"""

import streamlit as st

from app.styles.theme import apply_theme, CATEGORY_COLORS
from src.storage.store import list_available_dates, load_daily_report, load_scored_articles

# ---------------------------------------------------------------------------
# Page config (must be the first Streamlit command)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Insight Daily",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Apply theme
# ---------------------------------------------------------------------------

apply_theme()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### AI Insight Daily")
    st.caption("Bloomberg-style AI news intelligence")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # -- Date selector --
    available_dates = list_available_dates()

    if not available_dates:
        st.warning("No data available. Run the pipeline first.")
        st.stop()

    selected_date = st.selectbox(
        "DATE",
        options=available_dates,
        index=0,
    )

    # -- Load data --
    report = load_daily_report(selected_date)
    scored_articles = load_scored_articles(selected_date)

    # Store in session state for pages to access
    st.session_state["selected_date"] = selected_date
    st.session_state["report"] = report
    st.session_state["scored_articles"] = scored_articles

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # -- Category filter --
    all_categories = list(CATEGORY_COLORS.keys())
    selected_categories = st.multiselect(
        "CATEGORIES",
        options=all_categories,
        default=all_categories,
    )
    st.session_state["selected_categories"] = selected_categories

    # -- Minimum score slider --
    min_score = st.slider(
        "MINIMUM SCORE",
        min_value=1,
        max_value=10,
        value=1,
    )
    st.session_state["min_score"] = min_score

    # -- Language filter --
    language_filter = st.radio(
        "LANGUAGE",
        options=["All", "zh", "en"],
        index=0,
        horizontal=True,
    )
    st.session_state["language_filter"] = language_filter

    # -- Apply filters to scored articles --
    filtered_articles = scored_articles
    if filtered_articles:
        if selected_categories:
            filtered_articles = [
                a for a in filtered_articles
                if a.get("category") in selected_categories
            ]
        filtered_articles = [
            a for a in filtered_articles
            if a.get("impact_score", 0) >= min_score
        ]
        if language_filter != "All":
            filtered_articles = [
                a for a in filtered_articles
                if a.get("language") == language_filter
            ]
    st.session_state["filtered_articles"] = filtered_articles

    # -- Sidebar footer: pipeline status --
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    if report:
        st.caption(f"Report date: {report.get('report_date', '-')}")
        st.caption(f"Generated: {report.get('generated_at', '-')}")
        st.caption(
            f"Articles: {report.get('total_articles_processed', 0)} total, "
            f"{report.get('total_articles_after_filter', 0)} filtered"
        )
    st.caption(f"Showing: {len(filtered_articles)} articles")

# ---------------------------------------------------------------------------
# Main content area — landing page
# ---------------------------------------------------------------------------

if report is None:
    st.error(
        f"No report found for {selected_date}. "
        "Please run the pipeline to generate data."
    )
    st.stop()

# Redirect to daily report page by default
st.switch_page("pages/1_daily_report.py")
