"""Deduplicate articles based on title similarity."""

from __future__ import annotations

import jieba
from loguru import logger

from src.models.article import RawArticle


def _tokenize(title: str, language: str) -> set[str]:
    """Tokenize a title into a set of words.

    - Chinese (``zh``): use jieba word segmentation.
    - English (``en``): lowercase and split on whitespace.
    """
    if language == "zh":
        return set(jieba.lcut(title))
    return set(title.lower().split())


def _jaccard(set_a: set[str], set_b: set[str]) -> float:
    """Compute the Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def deduplicate(
    articles: list[RawArticle],
    threshold: float = 0.80,
) -> list[RawArticle]:
    """Remove near-duplicate articles based on title Jaccard similarity.

    For every pair of articles whose title token-set Jaccard similarity
    exceeds *threshold*, they are grouped as duplicates and only the one
    with the highest ``source_weight`` is kept.

    Parameters
    ----------
    articles : list[RawArticle]
        Input articles (order is preserved for non-duplicates).
    threshold : float
        Similarity threshold above which two articles are considered
        duplicates.  Default ``0.80``.

    Returns
    -------
    list[RawArticle]
        Deduplicated list.
    """
    if not articles:
        return []

    n = len(articles)
    token_sets = [_tokenize(a.title, a.language) for a in articles]

    # Union-Find to group duplicates -------------------------------------------
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i in range(n):
        for j in range(i + 1, n):
            if _jaccard(token_sets[i], token_sets[j]) > threshold:
                union(i, j)

    # Collect groups and pick the article with highest source_weight -----------
    groups: dict[int, list[int]] = {}
    for i in range(n):
        root = find(i)
        groups.setdefault(root, []).append(i)

    kept: list[RawArticle] = []
    for indices in groups.values():
        best_idx = max(indices, key=lambda i: articles[i].source_weight)
        kept.append(articles[best_idx])

    removed = n - len(kept)
    if removed:
        logger.info(
            "Deduplication removed {} duplicate(s) from {} articles",
            removed,
            n,
        )
    else:
        logger.info("No duplicates found among {} articles", n)

    return kept
