"""多日汇总报告生成器 — 聚合多天 scored 数据，复用现有 insight pipeline"""

import json
from datetime import date, timedelta
from pathlib import Path

from loguru import logger

from src.models.article import ScoredArticle
from src.models.report import DailyReport, DataFilterRules
from src.compute.cluster import build_filtered_context
from src.generation.insight_generator import generate_insights
from src.llm.client import ClaudeClient
from src.llm.prompts import PromptManager
from src.storage.store import list_available_dates

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "output"


def resolve_date_range(days: int, end_date: str | None = None) -> tuple[str, str]:
    """计算汇总日期范围，返回 (start_date, end_date) YYYY-MM-DD 字符串。"""
    end = date.fromisoformat(end_date) if end_date else date.today()
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def _load_scored_articles_for_range(start_date: str, end_date: str) -> tuple[list[ScoredArticle], list[str]]:
    """从磁盘加载日期范围内所有可用的 scored.json，合并为一个列表。

    Returns
    -------
    (articles, loaded_dates)
    """
    available = set(list_available_dates())

    start = date.fromisoformat(start_date)
    end   = date.fromisoformat(end_date)

    articles: list[ScoredArticle] = []
    loaded_dates: list[str] = []

    current = start
    while current <= end:
        ds = current.isoformat()
        if ds in available:
            scored_path = DATA_DIR / ds / "scored.json"
            if scored_path.exists():
                raw = json.loads(scored_path.read_text(encoding="utf-8"))
                day_articles = [ScoredArticle.model_validate(a) for a in raw]
                articles.extend(day_articles)
                loaded_dates.append(ds)
                logger.info(f"  Loaded {len(day_articles)} scored articles from {ds}")
            else:
                logger.warning(f"  scored.json missing for {ds}, skipping")
        else:
            logger.debug(f"  No report for {ds}, skipping")
        current += timedelta(days=1)

    return articles, loaded_dates


async def generate_period_summary(
    days: int,
    client: ClaudeClient,
    prompt_mgr: PromptManager,
    end_date: str | None = None,
    filter_rules: DataFilterRules | None = None,
) -> tuple[DailyReport, str, str]:
    """生成多日汇总报告，复用现有 insight 生成流程。

    Parameters
    ----------
    days : int
        汇总天数（3-5）。
    client : ClaudeClient
        LLM 客户端。
    prompt_mgr : PromptManager
        Prompt 模板管理器。
    end_date : str | None
        汇总截止日期 YYYY-MM-DD，默认为今天。
    filter_rules : DataFilterRules | None
        过滤规则，默认使用 top_k=10, min_impact_score=7。

    Returns
    -------
    (DailyReport, start_date, end_date)
        DailyReport.report_date 会被设为 "YYYY-MM-DD ~ YYYY-MM-DD" 格式。
    """
    start_date, end_date_resolved = resolve_date_range(days, end_date)
    period_label = f"{start_date} ~ {end_date_resolved}"
    logger.info(f"Generating period summary: {period_label}")

    # 1. 聚合多日 scored 数据
    all_articles, loaded_dates = _load_scored_articles_for_range(start_date, end_date_resolved)

    if not all_articles:
        raise RuntimeError(
            f"没有找到 {start_date} 至 {end_date_resolved} 范围内的任何 scored 数据。"
            f"请先运行 pipeline 生成各日日报。"
        )

    logger.info(f"  Aggregated {len(all_articles)} articles from {len(loaded_dates)} days: {loaded_dates}")

    # 2. 使用较大的 top_k（多日汇总展示更多事件）
    if filter_rules is None:
        filter_rules = DataFilterRules(top_k=10, min_impact_score=7)

    # source_weights 为空，多日汇总不再区分来源权重
    source_weights: dict[str, float] = {}

    # 3. 聚类 & 过滤（复用现有逻辑）
    filtered_context = build_filtered_context(all_articles, filter_rules, source_weights)
    logger.info(
        f"  Filtered: {filtered_context.total_after_filter}/{filtered_context.total_before_filter} "
        f"| Top: {len(filtered_context.top_events)}"
    )

    # 4. 调用 LLM 生成 insights（复用现有 insight prompt）
    report = await generate_insights(
        context=filtered_context,
        client=client,
        prompt_mgr=prompt_mgr,
        report_date=period_label,
        min_score=filter_rules.min_impact_score,
        top_k=filter_rules.top_k,
    )

    return report, start_date, end_date_resolved
