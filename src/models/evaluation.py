from pydantic import BaseModel, Field
from enum import Enum


class TargetDomain(str, Enum):
    SOFTWARE_ENGINEERING = "Software_Engineering"
    ML_SYSTEMS = "ML_Systems"
    GENERAL_AI = "General_AI"
    BUSINESS_ECOSYSTEM = "Business_Ecosystem"


class ScoreItem(BaseModel):
    """单项评分"""
    score: int = Field(ge=1, le=5)
    justification: str = Field(max_length=60, description="打分理由 (30字以内)")


class ImpactScoreItem(ScoreItem):
    """影响力评分 (附带 target_domain)"""
    target_domain: TargetDomain


class EvaluationMatrix(BaseModel):
    """Critic Agent 的三维评估矩阵"""

    technical_novelty: ScoreItem = Field(description="技术深度与新颖性 1-5")
    potential_impact: ImpactScoreItem = Field(description="潜在系统级影响力 1-5")
    readiness_level: ScoreItem = Field(description="技术成熟度 1-5")
    trend_insight: str | None = Field(
        default=None,
        description="基于评分推演的 1-3 个月趋势"
    )
    critical_risks: list[str] = Field(
        default_factory=list,
        description="潜在风险 (最多 2 条)"
    )
