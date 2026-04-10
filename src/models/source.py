from pydantic import BaseModel, Field
from enum import Enum


class ParserStrategy(str, Enum):
    FULL_TEXT = "full_text"
    SUMMARY_ONLY = "summary_only"


class SourceType(str, Enum):
    RSS = "rss"
    API = "api"
    STATIC = "static"


class SourceConfig(BaseModel):
    """信息源配置 — 描述一个新闻数据来源"""

    type: SourceType
    name: str = Field(description="信息源名称，如 'OpenAI Blog'")
    description: str = Field(default="", description="信息源描述")
    url: str = Field(description="数据源 URL")
    category: str = Field(description="信息源分类，如 'official', 'academic', 'community'")
    weight: float = Field(
        default=1.0, ge=0.5, le=2.0,
        description="信源权重因子。官方源 1.5, 普通博客 0.8, 默认 1.0"
    )
    parser_strategy: ParserStrategy = ParserStrategy.FULL_TEXT
    tags: list[str] = Field(default_factory=list)
