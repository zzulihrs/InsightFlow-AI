"""Clean and normalise raw article text."""

import re

from src.models.article import RawArticle


def clean_text(text: str) -> str:
    """Strip HTML tags, collapse whitespace, and trim a text string.

    Steps:
    1. Remove HTML tags via regex.
    2. Collapse consecutive whitespace characters (spaces, tabs, newlines)
       into a single space.
    3. Strip leading / trailing whitespace.
    """
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_articles(articles: list[RawArticle]) -> list[RawArticle]:
    """Return a new list of articles with cleaned *title* and *content*.

    Each article is copied via ``model_copy(update=...)`` so the originals
    are not mutated.
    """
    cleaned: list[RawArticle] = []
    for article in articles:
        cleaned.append(
            article.model_copy(
                update={
                    "title": clean_text(article.title),
                    "content": clean_text(article.content),
                }
            )
        )
    return cleaned
