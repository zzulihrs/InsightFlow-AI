from .source import SourceType, ParserStrategy, SourceConfig
from .article import (
    ArticleCategory, SentimentPolarity, RawArticle,
    StructuredAnalysis, StructuredArticle, ScoredArticle,
)
from .evaluation import (
    TargetDomain, ScoreItem, ImpactScoreItem, EvaluationMatrix,
)
from .report import (
    HotEvent, DeepDive, TrendInsight, RiskOpportunity,
    DailyReport, FilteredContext,
    AudiencePersona, DataFilterRules, ModuleConfig, ReportRule,
)

__all__ = [
    "SourceType", "ParserStrategy", "SourceConfig",
    "ArticleCategory", "SentimentPolarity", "RawArticle",
    "StructuredAnalysis", "StructuredArticle", "ScoredArticle",
    "TargetDomain", "ScoreItem", "ImpactScoreItem", "EvaluationMatrix",
    "HotEvent", "DeepDive", "TrendInsight", "RiskOpportunity",
    "DailyReport", "FilteredContext",
    "AudiencePersona", "DataFilterRules", "ModuleConfig", "ReportRule",
]
