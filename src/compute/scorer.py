"""Compute impact_score and final_score for scored articles."""

from loguru import logger

from src.models import ScoredArticle


def compute_scores(
    articles: list[ScoredArticle],
    source_weights: dict[str, float] | None = None,
) -> list[ScoredArticle]:
    """Compute impact_score and final_score for each article in place.

    impact_score is derived from the three-dimensional evaluation matrix:
        raw = novelty*0.35 + impact*0.45 + readiness*0.20
        impact_score = clamp(round(raw * 2), 1, 10)

    final_score = impact_score * source_weight.
    """
    for article in articles:
        ev = article.evaluation
        raw = (
            ev.technical_novelty.score * 0.35
            + ev.potential_impact.score * 0.45
            + ev.readiness_level.score * 0.20
        )
        article.impact_score = max(1, min(10, round(raw * 2)))

        # Override source_weight from external dict if provided
        if source_weights and article.source_name in source_weights:
            article.source_weight = source_weights[article.source_name]

        article.final_score = article.impact_score * article.source_weight

        logger.debug(
            "Scored article '{}': impact={}, weight={:.2f}, final={:.2f}",
            article.title,
            article.impact_score,
            article.source_weight,
            article.final_score,
        )

    logger.info("Computed scores for {} articles", len(articles))
    return articles
