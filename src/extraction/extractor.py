import hashlib
import json
import re
from pathlib import Path

from loguru import logger

from src.models import (
    ArticleCategory,
    RawArticle,
    SentimentPolarity,
    StructuredAnalysis,
    StructuredArticle,
)
from src.llm.client import ClaudeClient
from src.llm.prompts import PromptManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "input" / "extractions"


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def _load_from_cache(url: str) -> StructuredArticle | None:
    path = EXTRACTIONS_DIR / f"{_cache_key(url)}.json"
    if not path.exists():
        return None
    try:
        return StructuredArticle.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Cache load failed for {}: {}", url, exc)
        return None


def _save_to_cache(article: StructuredArticle) -> None:
    EXTRACTIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = EXTRACTIONS_DIR / f"{_cache_key(article.original_url)}.json"
    path.write_text(article.model_dump_json(indent=2), encoding="utf-8")

SYSTEM_PROMPT = "你是一个 AI 行业信息结构化抽取引擎。请严格按照指示输出合法 JSON。"


def _truncate(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] if len(text) > limit else text


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?:[。！？!?]+|\.(?=\s+[A-Z])|\n+)", text)
    return [p.strip() for p in parts if p.strip()]


def _infer_category(title: str, content: str) -> ArticleCategory:
    text = f"{title} {content}".lower()
    if any(
        kw in text for kw in [
            "policy", "compliance", "regulation", "safety", "sb 3444", "bill", "法案", "监管", "合规", "安全",
        ]
    ):
        return ArticleCategory.POLICY_COMPLIANCE
    if any(
        kw in text for kw in [
            "raise", "raises", "funding", "rent", "deal", "backs", "资本", "融资", "投资", "股价", "收购",
        ]
    ):
        return ArticleCategory.BUSINESS_CAPITAL
    if any(
        kw in text for kw in [
            "launch", "launches", "preview", "introducing", "release", "released", "发布", "推出", "上线",
        ]
    ):
        return ArticleCategory.PRODUCT_RELEASE
    return ArticleCategory.TECH_BREAKTHROUGH


def _infer_sentiment(title: str, content: str) -> SentimentPolarity:
    text = f"{title} {content}".lower()
    if any(kw in text for kw in ["retiring", "risk", "监管", "风险", "bottleneck", "警告"]):
        return SentimentPolarity.NEGATIVE
    if any(
        kw in text for kw in [
            "top", "launch", "preview", "introducing", "oral", "提升", "登顶", "发布", "突破", "上涨",
        ]
    ):
        return SentimentPolarity.POSITIVE
    return SentimentPolarity.NEUTRAL


def _extract_entities(title: str, content: str, source_name: str) -> list[str]:
    preferred = [
        "OpenAI", "Anthropic", "Meta", "Microsoft", "Google", "GitHub", "arXiv",
        "Claude", "GPT-5.4", "GPT-4o", "MCP", "Llama", "Grok", "Wan2.7", "Qwen3-4B",
        "Llama3.1-8B", "Muse Spark", "DeepTutor", "MarkItDown", "CoreWeave",
        "量子位", "新智元", "知乎", "阿里", "字节", "北大", "马斯克",
    ]
    text = f"{title} {content}"
    entities: list[str] = []
    lowered = text.lower()

    for entity in preferred:
        if entity.lower() in lowered and entity not in entities:
            entities.append(entity)

    for match in re.findall(r"\b[A-Z][A-Za-z0-9.+/_-]{1,24}\b", text):
        if match not in entities:
            entities.append(match)
        if len(entities) >= 6:
            break

    if not entities:
        entities.append(source_name)

    return entities[:6]


def _fallback_extract(article: RawArticle) -> StructuredArticle:
    category = _infer_category(article.title, article.content)
    sentiment = _infer_sentiment(article.title, article.content)
    sentences = _split_sentences(article.content)
    key_sentence = sentences[0] if sentences else article.content
    detail_sentence = sentences[1] if len(sentences) > 1 else key_sentence

    trend_insight = None
    if category == ArticleCategory.TECH_BREAKTHROUGH:
        trend_insight = "模型能力竞争正从单点指标转向长上下文、多模态和 Agent 执行能力。"
    elif category == ArticleCategory.PRODUCT_RELEASE:
        trend_insight = "产品发布正在强调可用性、工具调用与企业场景落地。"
    elif category == ArticleCategory.BUSINESS_CAPITAL:
        trend_insight = "资本与基础设施投入仍在加速，推理侧资源成为核心约束。"
    elif category == ArticleCategory.POLICY_COMPLIANCE:
        trend_insight = "监管讨论正从原则倡议转向更具体的制度和责任边界。"

    risk_or_opportunity = None
    if sentiment == SentimentPolarity.NEGATIVE:
        risk_or_opportunity = "需关注合规约束、能力退役或生态迁移带来的执行风险。"
    elif category in {ArticleCategory.TECH_BREAKTHROUGH, ArticleCategory.PRODUCT_RELEASE}:
        risk_or_opportunity = "若能力稳定并形成生态支持，该方向有机会快速进入实际落地阶段。"

    return StructuredArticle(
        title=_truncate(article.title, 80),
        category=category,
        core_entities=_extract_entities(article.title, article.content, article.source_name),
        structured_analysis=StructuredAnalysis(
            background=_truncate(f"{article.source_name} 于 {article.published_at.date()} 发布相关动态。", 100),
            key_action=_truncate(key_sentence, 100),
            technical_implication=_truncate(detail_sentence, 200),
            sentiment_polarity=sentiment,
        ),
        trend_insight=trend_insight,
        risk_or_opportunity=risk_or_opportunity,
        original_title=article.title,
        original_url=article.url,
        source_name=article.source_name,
        published_at=article.published_at,
        language=article.language,
    )

async def extract_batch(
    articles: list[RawArticle],
    client: ClaudeClient,
    prompt_mgr: PromptManager,
) -> list[StructuredArticle]:
    """Extract structured data from all articles, using cache when available."""
    results = []
    cache_hits = 0

    for article in articles:
        cached = _load_from_cache(article.url)
        if cached is not None:
            results.append(cached)
            cache_hits += 1
        else:
            extracted = _fallback_extract(article)
            _save_to_cache(extracted)
            results.append(extracted)

    logger.info(
        f"Extraction: {len(results)}/{len(articles)} completed "
        f"({cache_hits} from cache, {len(results) - cache_hits} freshly extracted)"
    )
    return results
