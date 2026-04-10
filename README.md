# InsightFlow-AI

InsightFlow-AI is an AI news analysis pipeline that ingests curated AI-related articles, performs structured extraction and multi-dimensional scoring, and generates a daily report in JSON, Markdown, and HTML.

## Key Features

- Multi-source AI news ingestion
- Structured extraction with schema-driven prompts
- Multi-dimensional event scoring
- Rule-based filtering and clustering
- Daily report generation
- Browser-friendly `report.html` output

## Project Structure

```text
config/      configuration files
data/        raw input data
prompts/     prompt templates
src/         core pipeline code
tests/       test suite
main.py      CLI entrypoint
```

## Run

```bash
python main.py --date 2026-04-11
```

Generated outputs are written under `data/output/<date>/`.
