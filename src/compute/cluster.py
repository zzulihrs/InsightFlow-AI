"""Cluster articles by category and compute entity frequency."""

import collections
from collections import defaultdict

from loguru import logger

from src.models import ScoredArticle, DataFilterRules, FilteredContext
from src.compute.scorer import compute_scores
from src.compute.filter import filter_articles


def cluster_articles(
    articles: list[ScoredArticle],
) -> tuple[dict[str, list[ScoredArticle]], list[tuple[str, int]]]:
    """Group articles by category and compute top-10 entity frequency.

    Returns:
        (clusters, entity_frequency)
    """
    # Group by category value
    clusters: dict[str, list[ScoredArticle]] = defaultdict(list)
    for article in articles:
        clusters[article.category.value].append(article)

    logger.info(
        "Clustered {} articles into {} categories: {}",
        len(articles),
        len(clusters),
        list(clusters.keys()),
    )

    # Count entity occurrences across all articles
    entity_counter: collections.Counter[str] = collections.Counter()
    for article in articles:
        entity_counter.update(article.core_entities)

    entity_frequency = entity_counter.most_common(10)
    logger.debug("Top entities: {}", entity_frequency)

    return dict(clusters), entity_frequency


def build_filtered_context(
    articles: list[ScoredArticle],
    rules: DataFilterRules,
    source_weights: dict[str, float] | None = None,
) -> FilteredContext:
    """Orchestrate the full compute pipeline: score -> filter -> cluster.

    Returns a fully populated FilteredContext.
    """
    total_before = len(articles)

    # Step 1: compute scores
    compute_scores(articles, source_weights)

    # Step 2: filter and rank
    top_events, all_filtered = filter_articles(articles, rules)

    # Step 3: cluster the filtered articles and compute entity frequency
    clusters, entity_frequency = cluster_articles(all_filtered)

    context = FilteredContext(
        top_events=top_events,
        all_filtered=all_filtered,
        clusters=clusters,
        entity_frequency=entity_frequency,
        total_before_filter=total_before,
        total_after_filter=len(all_filtered),
    )

    logger.info(
        "Built FilteredContext: {} -> {} articles, {} top events, {} clusters",
        total_before,
        len(all_filtered),
        len(top_events),
        len(clusters),
    )

    return context
