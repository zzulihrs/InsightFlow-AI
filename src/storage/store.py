"""Phase 7 — Storage: 日报数据持久化与索引管理"""

import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from src.models.report import DailyReport

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "output"


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

def save_daily_output(
    report_date: str,
    structured: list,
    scored: list,
    report: DailyReport,
    pipeline_log: dict,
) -> None:
    """将一次完整 Pipeline 运行的全部产出持久化到磁盘。

    Parameters
    ----------
    report_date : str
        日期字符串 YYYY-MM-DD，用作子目录名。
    structured : list
        StructuredArticle 列表 (Pydantic model 实例)。
    scored : list
        ScoredArticle 列表 (Pydantic model 实例)。
    report : DailyReport
        最终日报报告。
    pipeline_log : dict
        Pipeline 运行日志 / 元信息。
    """
    day_dir = DATA_DIR / report_date
    day_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Saving daily output to {day_dir}")

    # structured.json
    structured_path = day_dir / "structured.json"
    structured_path.write_text(
        json.dumps(
            [s.model_dump(mode="json") for s in structured],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.debug(f"Wrote {structured_path} ({len(structured)} articles)")

    # scored.json
    scored_path = day_dir / "scored.json"
    scored_path.write_text(
        json.dumps(
            [s.model_dump(mode="json") for s in scored],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.debug(f"Wrote {scored_path} ({len(scored)} articles)")

    # report.json
    report_path = day_dir / "report.json"
    report_path.write_text(
        json.dumps(
            report.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.debug(f"Wrote {report_path}")

    # report.md
    md_path = day_dir / "report.md"
    md_path.write_text(_generate_markdown(report), encoding="utf-8")
    logger.debug(f"Wrote {md_path}")

    # pipeline_log.json
    log_path = day_dir / "pipeline_log.json"
    log_path.write_text(
        json.dumps(pipeline_log, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    logger.debug(f"Wrote {log_path}")

    # 更新索引
    _update_index(report_date, report)

    # report.html — self-contained browser report
    try:
        from src.storage.html_generator import save_report_html
        report_dict  = json.loads(report_path.read_text(encoding="utf-8"))
        scored_dicts = json.loads(scored_path.read_text(encoding="utf-8"))
        html_path = save_report_html(report_date, report_dict, scored_dicts)
        logger.debug(f"Wrote {html_path}")
    except Exception as e:
        logger.warning(f"HTML generation failed (non-fatal): {e}")

    logger.info(f"Daily output saved successfully for {report_date}")


def load_daily_report(report_date: str) -> dict | None:
    """读取指定日期的 report.json，不存在则返回 None。"""
    path = DATA_DIR / report_date / "report.json"
    if not path.exists():
        logger.warning(f"Report not found: {path}")
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_scored_articles(report_date: str) -> list[dict]:
    """读取指定日期的 scored.json，不存在则返回空列表。"""
    path = DATA_DIR / report_date / "scored.json"
    if not path.exists():
        logger.warning(f"Scored articles not found: {path}")
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def list_available_dates() -> list[str]:
    """从 index.json 读取所有可用日期，按日期降序排列。"""
    index_path = DATA_DIR / "index.json"
    if not index_path.exists():
        return []
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        return [entry["date"] for entry in data.get("reports", [])]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to read index.json: {e}")
        return []


# ─────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────

def save_summary_output(
    start_date: str,
    end_date: str,
    report: DailyReport,
) -> Path:
    """将多日汇总报告持久化到磁盘。

    复用 DailyReport 结构，存入 summary_{start}_{end}/ 子目录。

    Parameters
    ----------
    start_date : str
        汇总起始日期 YYYY-MM-DD。
    end_date : str
        汇总结束日期 YYYY-MM-DD。
    report : DailyReport
        汇总报告（report_date 已设为 "start ~ end" 格式）。

    Returns
    -------
    Path
        保存目录路径。
    """
    dir_name = f"summary_{start_date}_{end_date}"
    summary_dir = DATA_DIR / dir_name
    summary_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Saving summary output to {summary_dir}")

    # report.json
    report_path = summary_dir / "report.json"
    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.debug(f"Wrote {report_path}")

    # report.html — 复用现有 HTML 生成器，period_label 已在 report_date 字段
    try:
        from src.storage.html_generator import save_report_html
        report_dict = json.loads(report_path.read_text(encoding="utf-8"))
        html_path = save_report_html(
            report.report_date,
            report_dict,
            [],           # scored 列表为空，汇总模式不需要 scored_map
            out_dir=summary_dir,
        )
        logger.debug(f"Wrote {html_path}")
    except Exception as e:
        logger.warning(f"Summary HTML generation failed (non-fatal): {e}")

    logger.info(f"Summary output saved for {start_date} ~ {end_date}")
    return summary_dir


def _generate_markdown(report: DailyReport) -> str:
    """将 DailyReport 转为可读的 Markdown 文本。"""
    lines: list[str] = []

    # Title
    lines.append(f"# AI Insight Daily — {report.report_date}")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    if report.executive_summary_zh:
        lines.append(f"**中文摘要：** {report.executive_summary_zh}")
        lines.append("")
    if report.executive_summary_en:
        lines.append(f"**English Summary:** {report.executive_summary_en}")
        lines.append("")

    # Hot Events
    if report.hot_events:
        lines.append("## Hot Events")
        lines.append("")
        for event in report.hot_events:
            score_badge = f"[⭐ {event.impact_score}.0/10]"
            url_part = f" — [{event.source_url}]({event.source_url})" if event.source_url else ""
            lines.append(f"### {event.rank}. {event.title} {score_badge}")
            lines.append("")
            lines.append(f"**分类：** {event.category}{url_part}")
            lines.append("")
            lines.append(event.summary)
            lines.append("")
            if event.background:
                lines.append("**背景：**")
                lines.append("")
                lines.append(event.background)
                lines.append("")
            if event.reference_links:
                lines.append("**参考资源：**")
                for ref in event.reference_links:
                    lines.append(f"- {ref}")
                lines.append("")
            if event.tags:
                lines.append(" ".join(event.tags))
                lines.append("")
            lines.append("---")
            lines.append("")

    # Deep Dives
    if report.deep_dives:
        lines.append("## Deep Dives")
        lines.append("")
        for dive in report.deep_dives:
            lines.append(f"### {dive.title}")
            lines.append("")
            lines.append(f"**Background:** {dive.background}")
            lines.append("")
            lines.append("**Key Findings:**")
            for finding in dive.key_findings:
                lines.append(f"- {finding}")
            lines.append("")
            lines.append(f"**Technical Impact:** {dive.technical_impact}")
            lines.append("")
            lines.append(f"**Business Impact:** {dive.business_impact}")
            lines.append("")
            lines.append(f"**Outlook:** {dive.outlook}")
            lines.append("")

    # Trend Insights
    if report.trend_insights:
        lines.append("## Trend Insights")
        lines.append("")
        for trend in report.trend_insights:
            confidence_label = f"[Confidence: {trend.confidence}]"
            lines.append(f"### {trend.trend_name} {confidence_label}")
            lines.append("")
            lines.append(trend.description)
            lines.append("")
            if trend.supporting_events:
                lines.append("Supporting events:")
                for evt in trend.supporting_events:
                    lines.append(f"- {evt}")
                lines.append("")

    # Risks & Opportunities
    if report.risks_and_opportunities:
        lines.append("## Risks & Opportunities")
        lines.append("")
        for item in report.risks_and_opportunities:
            icon = "Risk" if item.type == "risk" else "Opportunity"
            lines.append(f"- **[{icon}] {item.title}**: {item.description}")
            if item.related_events:
                lines.append(f"  - Related: {', '.join(item.related_events)}")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        f"*Generated at {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Processed: {report.total_articles_processed} articles | "
        f"After filter: {report.total_articles_after_filter}*"
    )
    lines.append("")

    return "\n".join(lines)


def _update_index(report_date: str, report: DailyReport) -> None:
    """更新 DATA_DIR/index.json — 维护全局日报索引。"""
    index_path = DATA_DIR / "index.json"

    # 读取现有索引
    if index_path.exists():
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to read existing index.json, creating new: {e}")
            data = {"reports": []}
    else:
        data = {"reports": []}

    # 计算平均分
    avg_score = 0.0
    if report.hot_events:
        avg_score = round(
            sum(e.impact_score for e in report.hot_events) / len(report.hot_events),
            2,
        )

    # 统计最多的 category
    top_category = ""
    if report.hot_events:
        category_counts: dict[str, int] = {}
        for event in report.hot_events:
            cat = event.category if isinstance(event.category, str) else event.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
        top_category = max(category_counts, key=category_counts.get)  # type: ignore[arg-type]

    # 构建本次条目
    entry = {
        "date": report_date,
        "summary_zh": report.executive_summary_zh[:50],
        "total_processed": report.total_articles_processed,
        "total_filtered": report.total_articles_after_filter,
        "avg_score": avg_score,
        "top_category": top_category,
        "generated_at": report.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 更新或插入
    reports: list[dict] = data.get("reports", [])
    existing_idx = next(
        (i for i, r in enumerate(reports) if r.get("date") == report_date),
        None,
    )
    if existing_idx is not None:
        reports[existing_idx] = entry
    else:
        reports.append(entry)

    # 按日期降序排列
    reports.sort(key=lambda r: r.get("date", ""), reverse=True)
    data["reports"] = reports

    # 写回
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.debug(f"Updated index.json ({len(reports)} entries)")
