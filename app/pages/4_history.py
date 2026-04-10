"""Phase 10 — History Page: 历史趋势与日报索引"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

from app.styles.theme import apply_theme, CHART_COLORS, PLOTLY_LAYOUT
from app.components.charts import create_history_line
from src.storage.store import DATA_DIR, list_available_dates, load_daily_report

# ─────────────────────────────────────────────────────────────
# Theme
# ─────────────────────────────────────────────────────────────
apply_theme()

# ─────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────
st.header("历史趋势")
st.caption("查看多日日报数据的趋势变化")

# ─────────────────────────────────────────────────────────────
# Load index data
# ─────────────────────────────────────────────────────────────
index_path = DATA_DIR / "index.json"
index_data: list[dict] = []

if index_path.exists():
    try:
        raw = json.loads(index_path.read_text(encoding="utf-8"))
        index_data = raw.get("reports", [])
    except (json.JSONDecodeError, OSError):
        index_data = []

if not index_data:
    st.info("暂无历史数据。请先运行 Pipeline 生成至少一天的日报。")
    st.stop()

# ─────────────────────────────────────────────────────────────
# Date range selector
# ─────────────────────────────────────────────────────────────
all_dates = sorted([d.get("date", "") for d in index_data if d.get("date")])

if not all_dates:
    st.warning("索引中没有有效的日期数据。")
    st.stop()

# Parse date strings for the date_input widgets
min_date = datetime.strptime(all_dates[0], "%Y-%m-%d").date()
max_date = datetime.strptime(all_dates[-1], "%Y-%m-%d").date()

st.subheader("日期范围筛选")
col_start, col_end = st.columns(2)
with col_start:
    start_date = st.date_input(
        "起始日期",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
    )
with col_end:
    end_date = st.date_input(
        "结束日期",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )

# Filter index data by selected date range
filtered_data = [
    d for d in index_data
    if d.get("date") and start_date <= datetime.strptime(d["date"], "%Y-%m-%d").date() <= end_date
]

# Sort chronologically for display
filtered_data.sort(key=lambda d: d.get("date", ""))

if not filtered_data:
    st.warning("所选日期范围内没有数据。")
    st.stop()

# ─────────────────────────────────────────────────────────────
# Summary metrics
# ─────────────────────────────────────────────────────────────
st.subheader("概览指标")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("覆盖天数", f"{len(filtered_data)} 天")
with m2:
    total_articles = sum(d.get("total_processed", 0) for d in filtered_data)
    st.metric("累计处理文章", f"{total_articles} 篇")
with m3:
    avg_scores = [d.get("avg_score", 0) for d in filtered_data if d.get("avg_score", 0) > 0]
    overall_avg = round(sum(avg_scores) / len(avg_scores), 2) if avg_scores else 0
    st.metric("整体平均评分", f"{overall_avg}")

# ─────────────────────────────────────────────────────────────
# History table
# ─────────────────────────────────────────────────────────────
st.subheader("日报索引一览")

table_rows = []
for entry in filtered_data:
    table_rows.append({
        "日期": entry.get("date", ""),
        "处理文章数": entry.get("total_processed", 0),
        "筛选后事件数": entry.get("total_filtered", 0),
        "平均评分": entry.get("avg_score", 0),
        "主要分类": entry.get("top_category", ""),
        "摘要": entry.get("summary_zh", ""),
    })

st.dataframe(
    table_rows,
    use_container_width=True,
    hide_index=True,
    column_config={
        "日期": st.column_config.TextColumn("日期", width="small"),
        "处理文章数": st.column_config.NumberColumn("处理文章数", width="small"),
        "筛选后事件数": st.column_config.NumberColumn("筛选后事件数", width="small"),
        "平均评分": st.column_config.NumberColumn("平均评分", format="%.2f", width="small"),
        "主要分类": st.column_config.TextColumn("主要分类", width="small"),
        "摘要": st.column_config.TextColumn("摘要", width="large"),
    },
)

# ─────────────────────────────────────────────────────────────
# History trend chart
# ─────────────────────────────────────────────────────────────
st.subheader("趋势变化")

if len(filtered_data) <= 1:
    st.info(
        "当前仅有 1 天的数据，趋势图需要至少 2 天的数据才能展示。"
        "请在不同日期多次运行 Pipeline 以积累历史数据。"
    )
else:
    fig_history = create_history_line(filtered_data)
    st.plotly_chart(fig_history, use_container_width=True)
