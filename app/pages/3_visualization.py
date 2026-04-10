"""Phase 10 — Visualization Page: 数据可视化分析仪表盘"""

import streamlit as st
from collections import Counter

from app.styles.theme import apply_theme, CHART_COLORS, PLOTLY_LAYOUT
from app.components.charts import (
    create_category_pie,
    create_score_distribution_bar,
    create_sentiment_bar,
    create_entity_frequency_bar,
    create_dimension_comparison_bar,
    create_timeline_scatter,
)

# ─────────────────────────────────────────────────────────────
# Theme
# ─────────────────────────────────────────────────────────────
apply_theme()

# ─────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────
st.header("数据可视化分析")
st.caption("多维度图表展示当日 AI 资讯评估结果")

# ─────────────────────────────────────────────────────────────
# Load data from session state
# ─────────────────────────────────────────────────────────────
scored_articles = st.session_state.get("scored_articles", [])

if not scored_articles:
    st.info("暂无数据。请先在首页选择日期加载日报数据。")
    st.stop()

# ─────────────────────────────────────────────────────────────
# Compute entity frequency
# ─────────────────────────────────────────────────────────────
entity_counter: Counter = Counter()
for article in scored_articles:
    entities = article.get("core_entities", [])
    if isinstance(entities, list):
        for entity in entities:
            if isinstance(entity, str) and entity.strip():
                entity_counter[entity.strip()] += 1
entity_frequency = entity_counter.most_common(10)

# ─────────────────────────────────────────────────────────────
# Row 1: Category Pie | Score Distribution
# ─────────────────────────────────────────────────────────────
st.subheader("分类与评分概览")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**文章分类分布**")
    fig_pie = create_category_pie(scored_articles)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("**影响力评分分布**")
    fig_score = create_score_distribution_bar(scored_articles)
    st.plotly_chart(fig_score, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# Row 2: Sentiment Bar | Entity Frequency
# ─────────────────────────────────────────────────────────────
st.subheader("情感与实体分析")

col3, col4 = st.columns(2)

with col3:
    st.markdown("**情感倾向分布**")
    fig_sentiment = create_sentiment_bar(scored_articles)
    st.plotly_chart(fig_sentiment, use_container_width=True)

with col4:
    st.markdown("**高频实体 Top 10**")
    fig_entity = create_entity_frequency_bar(entity_frequency)
    st.plotly_chart(fig_entity, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# Full-width: Dimension Comparison
# ─────────────────────────────────────────────────────────────
st.subheader("Top 事件多维评估对比")
fig_dim = create_dimension_comparison_bar(scored_articles, top_n=5)
st.plotly_chart(fig_dim, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# Full-width: Timeline Scatter
# ─────────────────────────────────────────────────────────────
st.subheader("事件时间轴")
fig_timeline = create_timeline_scatter(scored_articles)
st.plotly_chart(fig_timeline, use_container_width=True)
