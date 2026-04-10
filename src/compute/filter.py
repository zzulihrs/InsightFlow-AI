"""Filter and rank scored articles according to DataFilterRules."""

from loguru import logger

from src.models import ScoredArticle, DataFilterRules


def filter_articles(
    articles: list[ScoredArticle],
    rules: DataFilterRules,
) -> tuple[list[ScoredArticle], list[ScoredArticle]]:
    """Filter articles by impact_score and excluded categories, then rank.

    Returns:
        (top_events, all_filtered) where top_events is the top-K slice.
    """
    total_before = len(articles)

    # Sort by final_score descending
    sorted_articles = sorted(articles, key=lambda a: a.final_score, reverse=True)

    # Apply filters
    filtered = [
        a
        for a in sorted_articles
        if a.impact_score >= rules.min_impact_score
        and a.category.value not in rules.exclude_categories
    ]

    removed = total_before - len(filtered)
    logger.info(
        "Filtered articles: {} -> {} ({} removed, min_impact={}, excluded={})",
        total_before,
        len(filtered),
        removed,
        rules.min_impact_score,
        rules.exclude_categories,
    )

    top_events = filtered[: rules.top_k]
    return top_events, filtered
