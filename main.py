import argparse
import asyncio
import sys
from loguru import logger

# Configure loguru
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


def main():
    parser = argparse.ArgumentParser(description="Daily AI Insight Engine - Pipeline Runner")
    parser.add_argument("--date", type=str, default=None, help="Report date (YYYY-MM-DD), defaults to today")
    parser.add_argument(
        "--summary", type=int, default=None, metavar="N",
        help="生成最近 N 天的汇总日报（3-5），需已有各日日报数据"
    )
    parser.add_argument(
        "--summary-end-date", type=str, default=None, metavar="DATE",
        help="汇总截止日期 (YYYY-MM-DD)，配合 --summary 使用，默认为今天"
    )
    args = parser.parse_args()

    if args.summary is not None:
        _run_summary(args.summary, args.summary_end_date)
    else:
        _run_pipeline(args.date)


def _run_pipeline(report_date: str | None) -> None:
    from src.pipeline import run_pipeline

    try:
        result = asyncio.run(run_pipeline(report_date))
        html_path = f"data/output/{result['report_date']}/report.html"
        print(f"\n{'='*50}")
        print(f"Pipeline completed successfully!")
        print(f"Date:      {result['report_date']}")
        print(f"Duration:  {result['total_duration_s']}s")
        print(f"LLM calls: {result['total_llm_calls']}")
        print(f"HTML View: {html_path}")
        print(f"{'='*50}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


def _run_summary(days: int, end_date: str | None) -> None:
    import time
    from src.llm.client import ClaudeClient
    from src.llm.prompts import PromptManager
    from src.generation.summary_generator import generate_period_summary
    from src.storage.store import save_summary_output

    if days < 2:
        logger.error("--summary 天数至少为 2")
        sys.exit(1)

    client = ClaudeClient(max_concurrency=3)
    prompt_mgr = PromptManager()

    start_t = time.time()
    try:
        report, start_date, end_date_resolved = asyncio.run(
            generate_period_summary(days, client, prompt_mgr, end_date)
        )
        summary_dir = save_summary_output(start_date, end_date_resolved, report)
        html_path = summary_dir / "report.html"
        elapsed = round(time.time() - start_t, 2)
        print(f"\n{'='*50}")
        print(f"Period summary completed!")
        print(f"Period:    {start_date} ~ {end_date_resolved} ({days} days)")
        print(f"Duration:  {elapsed}s")
        print(f"LLM calls: {client.stats['total_calls']}")
        print(f"HTML View: {html_path}")
        print(f"{'='*50}")
    except Exception as e:
        logger.error(f"Summary failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
