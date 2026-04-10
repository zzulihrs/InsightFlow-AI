from pathlib import Path

from loguru import logger

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


class PromptManager:
    """Prompt 模板管理 — 加载和渲染 Prompt 模板"""

    def __init__(self, prompts_dir: Path | None = None):
        self.prompts_dir = prompts_dir or PROMPTS_DIR

    def load(self, template_name: str) -> str:
        """加载原始模板文本"""
        path = self.prompts_dir / f"{template_name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
        text = path.read_text(encoding="utf-8")
        logger.debug(f"Loaded prompt template: {template_name} ({len(text)} chars)")
        return text

    def render(self, template_name: str, **kwargs) -> str:
        """加载模板并渲染变量 (使用 str.format_map)"""
        template = self.load(template_name)
        try:
            return template.format_map(kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable in {template_name}: {e}")
            raise
