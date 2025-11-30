"""
单级分类工具
"""
from typing import List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from utils.llm_client import LLMClient
from prompts.classification import ClassificationPrompts
from config.settings import settings
from loguru import logger


class ClassifyLevelInput(BaseModel):
    """分类输入"""
    conversation: str = Field(description="清洗后的对话内容")
    available_categories: List[str] = Field(description="可选分类列表")
    current_path: List[str] = Field(default_factory=list, description="当前分类路径")
    level: int = Field(description="当前分类级别 (1/2/3)")


class ClassifyLevelTool(BaseTool):
    """单级分类工具"""
    name: str = "classify_level"
    description: str = "对对话进行单级分类决策"
    args_schema: type[BaseModel] = ClassifyLevelInput

    llm_client: LLMClient = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化LLM客户端（使用分类场景配置）
        self.llm_client = LLMClient.for_scenario("classification")

    def _run(
        self,
        conversation: str,
        available_categories: List[str],
        current_path: List[str] = None,
        level: int = 1
    ) -> str:
        """执行单级分类"""
        current_path = current_path or []
        max_retries = settings.classification_max_retries

        available_set = set(available_categories)

        for attempt in range(max_retries):
            # 生成提示词
            prompt = ClassificationPrompts.create_prompt(
                conversation=conversation,
                available_categories=available_categories,
                current_path=current_path,
                level=level
            )

            # 调用LLM
            messages = [{"role": "user", "content": prompt}]
            result = self.llm_client.chat_completion(
                messages=messages,
                max_tokens=settings.classification_max_tokens
            )

            category = result.strip()
            logger.info(f"分类结果: {category}")

            # 验证结果
            if category in available_set:
                return category

            logger.warning(
                f"分类结果 '{category}' 不在可选项中，"
                f"正在重试 ({attempt + 1}/{max_retries})"
            )

        # 多次重试后使用默认值
        logger.warning(f"多次重试后仍未得到有效分类，使用第一个选项")
        return available_categories[0]

    async def _arun(self, *args, **kwargs):
        """异步运行（暂不实现）"""
        raise NotImplementedError("异步模式暂未实现")
