"""Phase 9 -- Score badge rendering utilities."""

from __future__ import annotations


def get_score_color(score: int | float) -> str:
    """Return hex color string based on score range.

    8-10 -> green (#059669)
    5-7  -> amber (#D97706)
    1-4  -> red   (#DC2626)
    """
    s = float(score)
    if s >= 8:
        return "#059669"
    if s >= 5:
        return "#D97706"
    return "#DC2626"


def _score_css_class(score: int | float) -> str:
    s = float(score)
    if s >= 8:
        return "high"
    if s >= 5:
        return "mid"
    return "low"


def render_score_badge(score: int | float) -> str:
    """Return an HTML string for a colored score badge.

    The returned markup uses the .score-badge CSS class defined in theme.py.
    """
    css_cls = _score_css_class(score)
    # Display integer if the value is whole, otherwise one decimal
    display = str(int(score)) if float(score) == int(score) else f"{score:.1f}"
    return f'<span class="score-badge {css_cls}">{display}</span>'
