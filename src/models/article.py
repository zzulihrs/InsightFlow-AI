import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from enum import Enum

from .source import SourceType


class ArticleCategory(str, Enum):
    """新闻分类 — 四大类别"""
    TECH_BREAKTHROUGH = "技术突破"
    BUSINESS_CAPITAL = "商业资本"
    PRODUCT_RELEASE = "产品发布"
    POLICY_COMPLIANCE = "政策合规"


class SentimentPolarity(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class RawArticle(BaseModel):
    """从数据源获取的原始新闻数据"""

    source_name: str = Field(description="来源名称")
    source_type: SourceType = Field(default=SourceType.STATIC)
    title: str = Field(description="新闻标题")
    content: str = Field(description="正文内容或摘要")
    url: str = Field(description="原文链接")
    published_at: datetime = Field(description="发布时间")
    language: Literal["zh", "en"] = Field(description="语言")
    source_weight: float = Field(default=1.0, description="继承自信源配置的权重")


class StructuredAnalysis(BaseModel):
    """结构化分析 — LLM 抽取的深度字段"""

    background: str = Field(
        max_length=100,
        description="事件发生的背景 (50字以内)"
    )
    key_action: str = Field(
        max_length=100,
        description="核心动作/突破点 (50字以内)"
    )
    technical_implication: str = Field(
        max_length=200,
        description="对现有技术架构/开发流程的影响"
    )
    sentiment_polarity: SentimentPolarity


class StructuredArticle(BaseModel):
    """结构化抽取结果 — Extraction Agent 的输出"""

    article_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = Field(description="核心事件标题 (由 LLM 重新拟定，更精练)")
    category: ArticleCategory
    core_entities: list[str] = Field(
        min_length=1, max_length=10,
        description="实体列表 (公司名/产品名/技术名词)"
    )
    structured_analysis: StructuredAnalysis
    trend_insight: str | None = Field(
        default=None,
        description="该事件反映的行业趋势 (如无则 null)"
    )
    risk_or_opportunity: str | None = Field(
        default=None,
        description="潜在风险或机会 (如无则 null)"
    )

    # 保留原始数据引用
    original_title: str = Field(default="")
    original_url: str = Field(default="")
    source_name: str = Field(default="")
    published_at: datetime = Field(default_factory=datetime.now)
    language: Literal["zh", "en"] = Field(default="zh")


class ScoredArticle(StructuredArticle):
    """经过 Critic Agent 评分后的文章"""

    evaluation: "EvaluationMatrix"  # forward ref, resolved at runtime

    # 由代码计算的综合评分 (非 LLM 生成)
    impact_score: int = Field(
        default=0, ge=0, le=10,
        description="综合影响力评分 (1-10), 由三维评分加权计算"
    )
    final_score: float = Field(
        default=0.0,
        description="最终得分 = impact_score * source_weight"
    )
    source_weight: float = Field(default=1.0)


# Resolve forward reference after EvaluationMatrix is defined
from .evaluation import EvaluationMatrix  # noqa: E402
ScoredArticle.model_rebuild()
