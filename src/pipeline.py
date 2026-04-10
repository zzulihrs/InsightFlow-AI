import asyncio
import time
import uuid
import yaml
from datetime import date, datetime
from pathlib import Path
from loguru import logger

from src.models import ReportRule, DataFilterRules
from src.ingestion.loader import load_raw_articles
from src.ingestion.cleaner import clean_articles
from src.ingestion.dedup import deduplicate
from src.extraction.extractor import extract_batch
from src.extraction.critic import score_batch
from src.compute.cluster import build_filtered_context
from src.generation.insight_generator import generate_insights
from src.storage.store import save_daily_output
from src.llm.client import ClaudeClient
from src.llm.prompts import PromptManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_source_weights() -> dict[str, float]:
    """Load source weights from config/sources.yaml"""
    config_path = PROJECT_ROOT / "config" / "sources.yaml"
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {s["name"]: s.get("weight", 1.0) for s in data.get("sources", [])}


def _load_report_rules() -> ReportRule:
    """Load report rules from config/report_rules.yaml"""
    config_path = PROJECT_ROOT / "config" / "report_rules.yaml"
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ReportRule.model_validate(data)


async def run_pipeline(report_date: str | None = None) -> dict:
    """Run the full 6-stage pipeline"""
    if report_date is None:
        report_date = date.today().isoformat()

    run_id = str(uuid.uuid4())[:8]
    pipeline_log = {
        "run_id": run_id,
        "report_date": report_date,
        "started_at": datetime.now().isoformat(),
        "stages": {},
        "status": "running",
    }

    logger.info(f"=== Pipeline Start | date={report_date} | run_id={run_id} ===")

    # Load configs
    source_weights = _load_source_weights()
    rules = _load_report_rules()

    # Initialize LLM client and prompt manager
    client = ClaudeClient()
    prompt_mgr = PromptManager()

    total_start = time.time()

    try:
        # Stage 1: Ingestion
        stage_start = time.time()
        logger.info("Stage 1: Ingestion")
        raw_articles = load_raw_articles()
        cleaned = clean_articles(raw_articles)
        unique = deduplicate(cleaned)
        pipeline_log["stages"]["ingestion"] = {
            "input": len(raw_articles),
            "cleaned": len(cleaned),
            "output": len(unique),
            "deduped": len(cleaned) - len(unique),
            "duration_s": round(time.time() - stage_start, 2),
        }
        logger.info(f"  Ingested: {len(raw_articles)} -> cleaned: {len(cleaned)} -> unique: {len(unique)}")

        if not unique:
            raise RuntimeError("No articles after ingestion")

        # Stage 2: Extraction
        stage_start = time.time()
        logger.info("Stage 2: Extraction")
        structured = await extract_batch(unique, client, prompt_mgr)
        pipeline_log["stages"]["extraction"] = {
            "input": len(unique),
            "output": len(structured),
            "failed": len(unique) - len(structured),
            "duration_s": round(time.time() - stage_start, 2),
        }
        logger.info(f"  Extracted: {len(structured)}/{len(unique)}")

        if not structured:
            raise RuntimeError("All extractions failed")

        # Stage 3: Critic (Scoring)
        stage_start = time.time()
        logger.info("Stage 3: Critic")
        scored = await score_batch(structured, client, prompt_mgr)
        pipeline_log["stages"]["critic"] = {
            "input": len(structured),
            "output": len(scored),
            "duration_s": round(time.time() - stage_start, 2),
        }
        logger.info(f"  Scored: {len(scored)}/{len(structured)}")

        # Stage 4: Compute & Filter
        stage_start = time.time()
        logger.info("Stage 4: Compute & Filter")
        filtered_context = build_filtered_context(
            scored,
            rules.data_filter_rules,
            source_weights,
        )
        pipeline_log["stages"]["compute"] = {
            "input": len(scored),
            "output": filtered_context.total_after_filter,
            "filtered_out": filtered_context.total_before_filter - filtered_context.total_after_filter,
            "top_events": len(filtered_context.top_events),
            "duration_s": round(time.time() - stage_start, 2),
        }
        logger.info(f"  Filtered: {filtered_context.total_after_filter}/{len(scored)} | Top: {len(filtered_context.top_events)}")

        # Stage 5: Insight Generation
        stage_start = time.time()
        logger.info("Stage 5: Insight Generation")
        report = await generate_insights(
            context=filtered_context,
            client=client,
            prompt_mgr=prompt_mgr,
            report_date=report_date,
            min_score=rules.data_filter_rules.min_impact_score,
            top_k=rules.data_filter_rules.top_k,
        )
        pipeline_log["stages"]["insight"] = {
            "duration_s": round(time.time() - stage_start, 2),
        }
        logger.info(f"  Insight generated: {len(report.hot_events)} hot events, {len(report.trend_insights)} trends")

        # Stage 6: Report Assembly & Save
        stage_start = time.time()
        logger.info("Stage 6: Report Assembly")
        save_daily_output(report_date, structured, scored, report, pipeline_log)
        pipeline_log["stages"]["report"] = {
            "duration_s": round(time.time() - stage_start, 2),
        }

        pipeline_log["status"] = "success"
        pipeline_log["total_duration_s"] = round(time.time() - total_start, 2)
        pipeline_log["total_llm_calls"] = client.stats["total_calls"]
        pipeline_log["total_tokens"] = client.stats["total_tokens"]
        pipeline_log["finished_at"] = datetime.now().isoformat()

        # Re-save with complete log
        save_daily_output(report_date, structured, scored, report, pipeline_log)

        logger.info(f"=== Pipeline Complete | {pipeline_log['total_duration_s']}s | {client.stats['total_calls']} LLM calls ===")
        return pipeline_log

    except Exception as e:
        pipeline_log["status"] = "failed"
        pipeline_log["error"] = str(e)
        pipeline_log["total_duration_s"] = round(time.time() - total_start, 2)
        pipeline_log["finished_at"] = datetime.now().isoformat()
        logger.error(f"Pipeline failed: {e}")
        raise
