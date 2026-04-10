"""Phase 7 — Insight Generation: 调用 LLM 生成日报分析"""

import json
from datetime import datetime

from loguru import logger

from src.models.report import DailyReport, HotEvent, FilteredContext
from src.models.article import ScoredArticle
from src.llm.client import ClaudeClient
from src.llm.prompts import PromptManager

SYSTEM_PROMPT = (
    "你是一位在硅谷拥有十年经验的 AI 技术分析师。"
    "请严格按照指示输出合法 JSON。"
)


def _serialize_top_events(top_events: list[ScoredArticle]) -> str:
    """将 top_events 序列化为 JSON 字符串"""
    return json.dumps(
        [a.model_dump(mode="json") for a in top_events],
        ensure_ascii=False,
        indent=2,
    )


def _serialize_clusters(clusters: dict[str, list[ScoredArticle]]) -> str:
    """将 clusters 序列化为精简 JSON — 只保留关键字段以节省 token"""
    compact: dict[str, list[dict]] = {}
    for category, articles in clusters.items():
        compact[category] = [
            {
                "title": a.title,
                "impact_score": a.impact_score,
                "category": a.category.value if hasattr(a.category, "value") else str(a.category),
                "core_entities": a.core_entities,
            }
            for a in articles
        ]
    return json.dumps(compact, ensure_ascii=False, indent=2)


def _serialize_entity_frequency(entity_frequency: list[tuple[str, int]]) -> str:
    """将 entity_frequency 序列化为 JSON 字符串"""
    return json.dumps(entity_frequency, ensure_ascii=False)


def _strip_code_blocks(text: str) -> str:
    """去除 LLM 响应中可能包裹的 markdown 代码块标记"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _build_fallback_report(
    context: FilteredContext,
    report_date: str,
) -> DailyReport:
    """LLM 生成失败时，从 context 构建一份最小可用报告"""
    hot_events: list[HotEvent] = []
    for rank, article in enumerate(context.top_events, start=1):
        hot_events.append(
            HotEvent(
                rank=rank,
                title=article.title,
                impact_score=article.impact_score,
                category=article.category,
                summary=article.structured_analysis.key_action,
                source_url=article.original_url,
            )
        )

    return DailyReport(
        report_date=report_date,
        generated_at=datetime.now(),
        total_articles_processed=context.total_before_filter,
        total_articles_after_filter=context.total_after_filter,
        hot_events=hot_events,
        deep_dives=[],
        trend_insights=[],
        risks_and_opportunities=[],
        executive_summary_zh="[自动生成失败，以下为基于评分的热点事件列表]",
        executive_summary_en="[Auto-generation failed. Below is a score-based hot event list.]",
    )


async def generate_insights(
    context: FilteredContext,
    client: ClaudeClient,
    prompt_mgr: PromptManager,
    report_date: str,
    min_score: int = 7,
    top_k: int = 5,
) -> DailyReport:
    """调用 Claude 生成日报洞察分析，失败时回退为最小报告。

    Parameters
    ----------
    context : FilteredContext
        Compute 层输出的过滤 / 聚类上下文。
    client : ClaudeClient
        已初始化的 Claude 客户端。
    prompt_mgr : PromptManager
        Prompt 模板管理器。
    report_date : str
        报告日期，格式 YYYY-MM-DD。
    min_score : int
        过滤阈值 (仅用于渲染 prompt，不做实际过滤)。
    top_k : int
        Top K 事件数量。

    Returns
    -------
    DailyReport
    """
    # ── 1. 序列化上下文数据 ──────────────────────────────────
    top_events_json = _serialize_top_events(context.top_events)
    clusters_json = _serialize_clusters(context.clusters)
    entity_frequency_json = _serialize_entity_frequency(context.entity_frequency)

    # ── 2. 渲染 prompt ──────────────────────────────────────
    user_content = prompt_mgr.render(
        "insight",
        total_processed=context.total_before_filter,
        total_filtered=context.total_after_filter,
        min_score=min_score,
        report_date=report_date,
        top_k=top_k,
        top_events_json=top_events_json,
        clusters_json=clusters_json,
        entity_frequency_json=entity_frequency_json,
    )

    logger.info(
        f"Generating insights for {report_date} | "
        f"top_events={len(context.top_events)}, "
        f"clusters={len(context.clusters)}, "
        f"prompt_length={len(user_content)}"
    )

    # ── 3. 调用 LLM ─────────────────────────────────────────
    try:
        raw_response = await client.call(
            system_prompt=SYSTEM_PROMPT,
            user_content=user_content,
            max_tokens=4096,
        )

        # ── 4. 解析 JSON ────────────────────────────────────
        cleaned = _strip_code_blocks(raw_response)
        parsed = json.loads(cleaned)
        logger.debug(f"LLM response parsed successfully, keys={list(parsed.keys())}")

        # ── 5. 构建 DailyReport ─────────────────────────────
        report = DailyReport(
            report_date=report_date,
            generated_at=datetime.now(),
            total_articles_processed=context.total_before_filter,
            total_articles_after_filter=context.total_after_filter,
            hot_events=parsed.get("hot_events", []),
            deep_dives=parsed.get("deep_dives", []),
            trend_insights=parsed.get("trend_insights", []),
            risks_and_opportunities=parsed.get("risks_and_opportunities", []),
            executive_summary_zh=parsed.get("executive_summary_zh", ""),
            executive_summary_en=parsed.get("executive_summary_en", ""),
        )

        logger.info(
            f"Insight generation complete | "
            f"hot_events={len(report.hot_events)}, "
            f"deep_dives={len(report.deep_dives)}, "
            f"trend_insights={len(report.trend_insights)}"
        )
        return report

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.debug(f"Raw response (first 500 chars): {raw_response[:500]}")
        return _build_fallback_report(context, report_date)

    except Exception as e:
        logger.error(f"Insight generation failed: {e}")
        return _build_fallback_report(context, report_date)
