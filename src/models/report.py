from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from .article import ArticleCategory, ScoredArticle


class HotEvent(BaseModel):
    """热点事件摘要"""
    rank: int
    title: str
    impact_score: int
    category: ArticleCategory
    summary: str = Field(description="2-3句话概要，说明发生了什么及重要意义")
    source_url: str
    background: str = Field(default="", description="背景说明，解释相关技术术语和上下文")
    tags: list[str] = Field(default_factory=list, description="话题标签列表，如 #AI #LLM")
    reference_links: list[str] = Field(default_factory=list, description="相关参考资源描述列表")


class DeepDive(BaseModel):
    """重要事件深度分析"""
    title: str
    background: str
    key_findings: list[str]
    technical_impact: str
    business_impact: str
    outlook: str


class TrendInsight(BaseModel):
    """趋势洞察"""
    trend_name: str
    description: str
    supporting_events: list[str] = Field(description="支撑该趋势的事件标题列表")
    confidence: Literal["高", "中", "低"]


class RiskOpportunity(BaseModel):
    """风险与机会"""
    type: Literal["risk", "opportunity"]
    title: str
    description: str
    related_events: list[str]


class DailyReport(BaseModel):
    """完整的日报报告"""

    report_date: str = Field(description="日报日期 YYYY-MM-DD")
    generated_at: datetime = Field(default_factory=datetime.now)

    # 元信息
    total_articles_processed: int = 0
    total_articles_after_filter: int = 0

    # 报告内容
    hot_events: list[HotEvent] = Field(default_factory=list, description="Top 3-5 热点事件")
    deep_dives: list[DeepDive] = Field(default_factory=list, description="1-2 个重要事件深度分析")
    trend_insights: list[TrendInsight] = Field(default_factory=list, description="趋势判断")
    risks_and_opportunities: list[RiskOpportunity] = Field(
        default_factory=list,
        description="风险与机会 (可选)"
    )

    # 双语摘要
    executive_summary_zh: str = Field(default="", description="中文执行摘要 (200字以内)")
    executive_summary_en: str = Field(default="", description="英文执行摘要 (150 words)")


class FilteredContext(BaseModel):
    """Compute 层输出 — 过滤和聚类后的上下文"""

    top_events: list[ScoredArticle] = Field(default_factory=list)
    all_filtered: list[ScoredArticle] = Field(default_factory=list)
    clusters: dict[str, list[ScoredArticle]] = Field(default_factory=dict)
    entity_frequency: list[tuple[str, int]] = Field(default_factory=list)
    total_before_filter: int = 0
    total_after_filter: int = 0


class AudiencePersona(BaseModel):
    role: str = "资深后端工程师与 AI Agent 开发者"
    tone: str = "客观、极客、直击痛点，拒绝营销话术"
    focus_domain: list[str] = Field(
        default_factory=lambda: ["技术突破", "开源框架", "模型微调", "API降价"]
    )


class DataFilterRules(BaseModel):
    top_k: int = Field(default=5, description="提取 impact_score 最高的 K 条")
    min_impact_score: int = Field(default=7, description="过滤低于该分值的新闻")
    exclude_categories: list[str] = Field(default_factory=list)


class ModuleConfig(BaseModel):
    enabled: bool = True
    format: Literal["bullet_points", "deep_dive"] = "bullet_points"
    require_tech_details: bool = True


class ReportRule(BaseModel):
    """报告配置规则 — 控制日报的生成行为"""

    profile_name: str = "Developer_Daily_Brief"
    audience_persona: AudiencePersona = Field(default_factory=AudiencePersona)
    data_filter_rules: DataFilterRules = Field(default_factory=DataFilterRules)

    module_configs: dict[str, ModuleConfig] = Field(
        default_factory=lambda: {
            "hot_events": ModuleConfig(enabled=True, format="bullet_points"),
            "trend_insight": ModuleConfig(enabled=True),
            "risk_and_opportunity": ModuleConfig(enabled=True),
        }
    )
