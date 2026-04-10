"""Phase 5 — Insight Generation

使用两次独立的 LLM 调用，避免单次大 JSON 响应超出代理超时限制：
  Call 1 (insight_hot.txt)      → 生成 hot_events（带背景/标签/参考链接）
  Call 2 (insight_analysis.txt) → 生成 deep_dives / trend_insights / risks / executive_summary
"""

import json
from datetime import datetime

from loguru import logger

from src.models.report import DailyReport, HotEvent, FilteredContext
from src.models.article import ScoredArticle
from src.llm.client import ClaudeClient
from src.llm.prompts import PromptManager

SYSTEM_PROMPT = (
    "你是一位在硅谷拥有十年经验的 AI 技术分析师，精通中英双语。"
    "请严格按照指示输出合法 JSON，不要添加任何前言后语。"
)


# ── Serializers ───────────────────────────────────────────────────────────────

def _serialize_top_events(top_events: list[ScoredArticle]) -> str:
    """精简序列化 — 只保留 LLM 所需核心字段，降低 token 消耗。"""
    slim = []
    for a in top_events:
        cat = a.category.value if hasattr(a.category, "value") else str(a.category)
        slim.append({
            "title":         a.title,
            "category":      cat,
            "impact_score":  a.impact_score,
            "source_name":   a.source_name,
            "original_url":  a.original_url,
            "core_entities": a.core_entities[:4],
            "background":    a.structured_analysis.background,
            "key_action":    a.structured_analysis.key_action,
            "tech_impact":   a.structured_analysis.technical_implication[:80],
            "trend_insight": (a.trend_insight or "")[:60],
        })
    return json.dumps(slim, ensure_ascii=False, indent=2)


def _top_events_brief(top_events: list[ScoredArticle]) -> str:
    """仅含标题、分类、评分的极简列表，用于 analysis call。"""
    lines = []
    for i, a in enumerate(top_events, 1):
        cat = a.category.value if hasattr(a.category, "value") else str(a.category)
        lines.append(f"{i}. [{cat}·{a.impact_score}分] {a.title}")
    return "\n".join(lines)


def _clusters_brief(clusters: dict[str, list[ScoredArticle]]) -> str:
    """各分类的事件计数，极简格式。"""
    parts = [f"{cat}: {len(arts)}条" for cat, arts in clusters.items()]
    return " | ".join(parts)


def _serialize_entity_frequency(entity_frequency: list[tuple[str, int]]) -> str:
    return json.dumps(entity_frequency[:8], ensure_ascii=False)


def _strip_json(text: str) -> str:
    text = text.strip()
    for prefix in ("```json", "```"):
        if text.startswith(prefix):
            text = text[len(prefix):]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


# ── Fallback ──────────────────────────────────────────────────────────────────

def _build_fallback_report(context: FilteredContext, report_date: str) -> DailyReport:
    hot_events: list[HotEvent] = []
    for rank, article in enumerate(context.top_events, start=1):
        cat_str = (
            article.category.value
            if hasattr(article.category, "value")
            else str(article.category)
        )
        hot_events.append(
            HotEvent(
                rank=rank,
                title=article.title,
                impact_score=article.impact_score,
                category=article.category,
                summary=article.structured_analysis.key_action,
                source_url=article.original_url,
                background=article.structured_analysis.background,
                tags=[f"#{cat_str}"] + [f"#{e}" for e in article.core_entities[:3]],
                reference_links=[],
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
        executive_summary_zh="",
        executive_summary_en="",
    )


# ── Main ──────────────────────────────────────────────────────────────────────

async def generate_insights(
    context: FilteredContext,
    client: ClaudeClient,
    prompt_mgr: PromptManager,
    report_date: str,
    min_score: int = 7,
    top_k: int = 5,
) -> DailyReport:
    """两步 LLM 生成：Call 1 → hot_events；Call 2 → deep_dives/trends/risks/summary。"""

    top_events_json   = _serialize_top_events(context.top_events)
    top_brief         = _top_events_brief(context.top_events)
    clusters_brief    = _clusters_brief(context.clusters)
    entity_freq_json  = _serialize_entity_frequency(context.entity_frequency)

    logger.info(
        f"Generating insights for {report_date} | "
        f"top_events={len(context.top_events)}, clusters={len(context.clusters)}"
    )

    # ── Call 1: hot events ────────────────────────────────────────────────────
    # Use actual article count to avoid asking LLM for more items than available
    effective_top_k = min(top_k, len(context.top_events))
    hot_events: list[HotEvent] = []
    try:
        prompt_hot = prompt_mgr.render(
            "insight_hot",
            top_k=effective_top_k,
            top_events_json=top_events_json,
        )
        logger.info(f"  Call 1 (hot_events) | prompt={len(prompt_hot)} chars")
        raw1 = await client.call(SYSTEM_PROMPT, prompt_hot, max_retries=1)
        cleaned1 = _strip_json(raw1)

        # Parse: accept array [ ] or {"hot_events": [...]}
        try:
            items = json.loads(cleaned1)
        except json.JSONDecodeError:
            # Attempt to extract from partial response
            from src.llm.client import _extract_json
            cleaned1 = _extract_json(cleaned1)
            items = json.loads(cleaned1)

        if isinstance(items, dict):
            items = items.get("hot_events", [])
        hot_events = items
        logger.info(f"  Call 1 OK | {len(hot_events)} hot events")

        if len(hot_events) == 0:
            logger.warning("Call 1 returned 0 hot events — using structured fallback")
            hot_events = _build_fallback_report(context, report_date).hot_events

    except Exception as e:
        logger.error(f"Call 1 (hot_events) failed: {e}")
        return _build_fallback_report(context, report_date)

    # ── Call 2: analysis (deep_dives / trends / risks / summary) ────────────────
    deep_dives: list = []
    trend_insights: list = []
    risks_and_opportunities: list = []
    executive_summary_zh = ""
    executive_summary_en = ""
    try:
        prompt_analysis = prompt_mgr.render(
            "insight_analysis",
            report_date=report_date,
            total_processed=context.total_before_filter,
            total_filtered=context.total_after_filter,
            top_events_json=top_events_json,
            clusters_brief=clusters_brief,
            entity_frequency_json=entity_freq_json,
        )
        logger.info(f"  Call 2 (analysis) | prompt={len(prompt_analysis)} chars")
        raw2 = await client.call(SYSTEM_PROMPT, prompt_analysis, max_retries=1)
        parsed2 = json.loads(_strip_json(raw2))
        deep_dives              = parsed2.get("deep_dives", [])
        trend_insights          = parsed2.get("trend_insights", [])
        risks_and_opportunities = parsed2.get("risks_and_opportunities", [])
        executive_summary_zh    = parsed2.get("executive_summary_zh", "")
        executive_summary_en    = parsed2.get("executive_summary_en", "")
        logger.info(
            f"  Call 2 OK | {len(deep_dives)} deep_dives, "
            f"{len(trend_insights)} trends, "
            f"{len(risks_and_opportunities)} risks"
        )
    except Exception as e:
        logger.warning(f"Call 2 (analysis) failed (non-fatal): {e}")
        # Analysis failure is non-fatal — hot events are already generated

    report = DailyReport(
        report_date=report_date,
        generated_at=datetime.now(),
        total_articles_processed=context.total_before_filter,
        total_articles_after_filter=context.total_after_filter,
        hot_events=hot_events,
        deep_dives=deep_dives,
        trend_insights=trend_insights,
        risks_and_opportunities=risks_and_opportunities,
        executive_summary_zh=executive_summary_zh,
        executive_summary_en=executive_summary_en,
    )

    logger.info(
        f"Insight generation complete | "
        f"hot={len(hot_events)}, trends={len(trend_insights)}, "
        f"risks={len(risks_and_opportunities)}"
    )
    return report
