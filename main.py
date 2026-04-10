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
    args = parser.parse_args()

    from src.pipeline import run_pipeline

    try:
        result = asyncio.run(run_pipeline(args.date))
        print(f"\n{'='*50}")
        print(f"Pipeline completed successfully!")
        print(f"Date: {result['report_date']}")
        print(f"Duration: {result['total_duration_s']}s")
        print(f"LLM calls: {result['total_llm_calls']}")
        print(f"Status: {result['status']}")
        print(f"{'='*50}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
