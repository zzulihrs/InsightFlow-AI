"""Load raw articles from the JSON data file."""

import json
from pathlib import Path

from loguru import logger

from src.models.article import RawArticle

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "input" / "raw_news.json"


def load_raw_articles(data_path: str | Path = None) -> list[RawArticle]:
    """Read *raw_news.json* and return a list of validated RawArticle objects.

    Parameters
    ----------
    data_path : str | Path, optional
        Path to the JSON file.  Defaults to ``data/raw/raw_news.json``
        relative to the project root.

    Returns
    -------
    list[RawArticle]

    Raises
    ------
    FileNotFoundError
        If the JSON file does not exist at the resolved path.
    """
    path = Path(data_path) if data_path is not None else DEFAULT_DATA_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"Raw news file not found: {path}. "
            "Please ensure the data file exists before loading."
        )

    raw_data = json.loads(path.read_text(encoding="utf-8"))

    articles: list[RawArticle] = []
    for idx, item in enumerate(raw_data):
        try:
            articles.append(RawArticle.model_validate(item))
        except Exception as exc:
            logger.warning(
                "Skipping item #{} due to validation error: {}", idx, exc
            )

    logger.info("Loaded {} raw articles from {}", len(articles), path)
    return articles
