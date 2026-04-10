import asyncio
import json
import unittest
from pathlib import Path

from src.pipeline import run_pipeline


class PipelineOfflineTest(unittest.TestCase):
    def test_pipeline_generates_output_files(self) -> None:
        # No date specified — auto-detected from latest article in data/input/raw_news.json
        result = asyncio.run(run_pipeline())

        self.assertEqual(result["status"], "success")
        report_date = result["report_date"]

        output_dir = Path("data") / "output" / report_date
        expected_files = [
            "structured.json",
            "scored.json",
            "report.json",
            "report.md",
            "pipeline_log.json",
            "report.html",
        ]
        for filename in expected_files:
            self.assertTrue((output_dir / filename).exists(), filename)

        report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
        scored = json.loads((output_dir / "scored.json").read_text(encoding="utf-8"))

        self.assertEqual(report["report_date"], report_date)
        self.assertGreaterEqual(len(scored), 1)
        self.assertGreaterEqual(report["total_articles_processed"], report["total_articles_after_filter"])
        self.assertIn("executive_summary_zh", report)


if __name__ == "__main__":
    unittest.main()
