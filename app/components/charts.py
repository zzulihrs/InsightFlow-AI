"""Phase 9+10 -- Chart components: radar chart + full visualization suite."""

from __future__ import annotations

from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.styles.theme import CHART_COLORS, PLOTLY_LAYOUT


# ─────────────────────────────────────────────────────────────
# Radar Chart (Phase 9)
# ─────────────────────────────────────────────────────────────

def create_radar_chart(evaluation: dict) -> go.Figure:
    """Create a Plotly radar (Scatterpolar) chart for the three evaluation
    dimensions: technical_novelty, potential_impact, readiness_level.

    Parameters
    ----------
    evaluation : dict
        The ``evaluation`` dict from a scored article.  Each dimension is a
        sub-dict with at least a ``score`` (int 1-5) key.

    Returns
    -------
    go.Figure
    """
    dimension_labels = ["技术新颖性", "影响力", "成熟度"]
    dimension_keys = ["technical_novelty", "potential_impact", "readiness_level"]

    values: list[int] = []
    for key in dimension_keys:
        dim = evaluation.get(key, {})
        if isinstance(dim, dict):
            values.append(dim.get("score", 0))
        else:
            values.append(0)

    # Close the polygon by repeating the first value
    radar_values = values + [values[0]]
    radar_labels = dimension_labels + [dimension_labels[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=radar_values,
            theta=radar_labels,
            fill="toself",
            fillcolor="rgba(37, 99, 235, 0.15)",
            line=dict(color=CHART_COLORS["primary"], width=2),
            marker=dict(size=6, color=CHART_COLORS["primary"]),
            name="Evaluation",
        )
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                tickfont=dict(size=11, color="#4A5568"),
                gridcolor="#E2E8F0",
                linecolor="#E2E8F0",
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color="#1A1A2E"),
                gridcolor="#E2E8F0",
                linecolor="#E2E8F0",
            ),
        ),
        showlegend=False,
        height=320,
        width=360,
    )

    return fig


# ─────────────────────────────────────────────────────────────
# Category Pie Chart (Phase 10)
# ─────────────────────────────────────────────────────────────

def create_category_pie(scored_articles: list[dict]) -> go.Figure:
    """Pie chart of article count by category."""
    cats = Counter(a.get("category", "未知") for a in scored_articles)
    labels = list(cats.keys())
    values = list(cats.values())
    colors = [CHART_COLORS["category_map"].get(l, "#6C757D") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        textinfo="label+percent",
        hole=0.4,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=True, title=None, height=350)
    return fig


# ─────────────────────────────────────────────────────────────
# Score Distribution Bar (Phase 10)
# ─────────────────────────────────────────────────────────────

def create_score_distribution_bar(scored_articles: list[dict]) -> go.Figure:
    """Bar chart with score buckets (1-3, 4-6, 7-8, 9-10)."""
    buckets = {"1-3": 0, "4-6": 0, "7-8": 0, "9-10": 0}
    for a in scored_articles:
        s = a.get("impact_score", 0)
        if s <= 3:
            buckets["1-3"] += 1
        elif s <= 6:
            buckets["4-6"] += 1
        elif s <= 8:
            buckets["7-8"] += 1
        else:
            buckets["9-10"] += 1

    colors = [
        CHART_COLORS["danger"],
        CHART_COLORS["warning"],
        CHART_COLORS["primary"],
        CHART_COLORS["success"],
    ]

    fig = go.Figure(go.Bar(
        x=list(buckets.keys()),
        y=list(buckets.values()),
        marker_color=colors,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="评分区间", yaxis_title="数量", height=350)
    return fig


# ─────────────────────────────────────────────────────────────
# Sentiment Bar (Phase 10)
# ─────────────────────────────────────────────────────────────

def create_sentiment_bar(scored_articles: list[dict]) -> go.Figure:
    """Horizontal bar of sentiment polarity counts."""
    sentiments: Counter = Counter()
    for a in scored_articles:
        sa = a.get("structured_analysis", {})
        sentiments[sa.get("sentiment_polarity", "Neutral")] += 1

    labels = ["Positive", "Neutral", "Negative"]
    values = [sentiments.get(l, 0) for l in labels]
    colors = [CHART_COLORS["sentiment_map"].get(l, "#6C757D") for l in labels]

    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="数量", height=300)
    return fig


# ─────────────────────────────────────────────────────────────
# Entity Frequency Bar (Phase 10)
# ─────────────────────────────────────────────────────────────

def create_entity_frequency_bar(entity_freq: list) -> go.Figure:
    """Horizontal bar chart of top entities."""
    if not entity_freq:
        fig = go.Figure()
        fig.update_layout(**PLOTLY_LAYOUT, height=350)
        return fig

    labels = [item[0] for item in reversed(entity_freq[:10])]
    values = [item[1] for item in reversed(entity_freq[:10])]

    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation="h",
        marker_color=CHART_COLORS["primary"],
    ))
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="出现次数", height=350)
    return fig


# ─────────────────────────────────────────────────────────────
# Dimension Comparison Grouped Bar (Phase 10)
# ─────────────────────────────────────────────────────────────

def create_dimension_comparison_bar(scored_articles: list[dict], top_n: int = 5) -> go.Figure:
    """Grouped bar chart of 3 eval dimensions per event (top N by final_score)."""
    sorted_arts = sorted(
        scored_articles,
        key=lambda a: a.get("final_score", 0),
        reverse=True,
    )[:top_n]

    titles = [a.get("title", "")[:15] + "..." for a in sorted_arts]
    novelty = [
        a.get("evaluation", {}).get("technical_novelty", {}).get("score", 0)
        for a in sorted_arts
    ]
    impact = [
        a.get("evaluation", {}).get("potential_impact", {}).get("score", 0)
        for a in sorted_arts
    ]
    readiness = [
        a.get("evaluation", {}).get("readiness_level", {}).get("score", 0)
        for a in sorted_arts
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="技术新颖性", x=titles, y=novelty, marker_color=CHART_COLORS["primary"]))
    fig.add_trace(go.Bar(name="影响力", x=titles, y=impact, marker_color=CHART_COLORS["success"]))
    fig.add_trace(go.Bar(name="成熟度", x=titles, y=readiness, marker_color=CHART_COLORS["warning"]))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        barmode="group",
        yaxis_title="评分 (1-5)",
        height=400,
        legend=dict(orientation="h", y=1.1),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Timeline Scatter (Phase 10)
# ─────────────────────────────────────────────────────────────

def create_timeline_scatter(scored_articles: list[dict]) -> go.Figure:
    """Scatter plot: time x score, size=impact, color=category."""
    if not scored_articles:
        fig = go.Figure()
        fig.update_layout(**PLOTLY_LAYOUT, height=400)
        return fig

    df = pd.DataFrame([{
        "title": a.get("title", ""),
        "published_at": a.get("published_at", ""),
        "impact_score": a.get("impact_score", 0),
        "final_score": max(a.get("final_score", 1), 1),
        "category": a.get("category", "未知"),
    } for a in scored_articles])
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")

    fig = px.scatter(
        df,
        x="published_at",
        y="impact_score",
        size="final_score",
        color="category",
        hover_name="title",
        color_discrete_map=CHART_COLORS["category_map"],
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="发布时间",
        yaxis_title="影响力评分",
        height=400,
    )
    return fig


# ─────────────────────────────────────────────────────────────
# History Line Chart (Phase 10)
# ─────────────────────────────────────────────────────────────

def create_history_line(index_data: list[dict]) -> go.Figure:
    """Line chart of daily avg score over time (dual Y-axis)."""
    if not index_data:
        fig = go.Figure()
        fig.update_layout(**PLOTLY_LAYOUT, height=350)
        return fig

    dates = [d.get("date", "") for d in index_data]
    avg_scores = [d.get("avg_score", 0) for d in index_data]
    counts = [d.get("total_filtered", 0) for d in index_data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=avg_scores,
        name="平均评分",
        line=dict(color=CHART_COLORS["primary"]),
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=counts,
        name="高分事件数",
        line=dict(color=CHART_COLORS["success"]),
        yaxis="y2",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=350,
        yaxis=dict(title="平均评分"),
        yaxis2=dict(title="事件数", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1),
    )
    return fig
