"""
单级分类工具
"""
from typing import List, Optional, Dict
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from utils.llm_client import LLMClient
from prompts.classification import ClassificationPrompts
from models.schemas import CategoryData
from config.settings import settings
from loguru import logger


class ClassifyLevelInput(BaseModel):
    """分类输入"""
    conversation: str = Field(description="清洗后的对话内容")
    available_categories: List[str] = Field(description="可选分类列表")
    current_path: List[str] = Field(default_factory=list, description="当前分类路径")
    level: int = Field(description="当前分类级别 (1/2/3)")
    chat_history: List[Dict] = Field(default_factory=list, description="对话历史")


class ClassifyLevelTool(BaseTool):
    """单级分类工具"""
    name: str = "classify_level"
    description: str = "对对话进行单级分类决策"
    args_schema: type[BaseModel] = ClassifyLevelInput

    llm_client: LLMClient = None
    categories: Optional[CategoryData] = None

    def __init__(self, categories: Optional[CategoryData] = None, **kwargs):
        super().__init__(**kwargs)
        # 初始化LLM客户端（使用分类场景配置）
        self.llm_client = LLMClient.for_scenario("classification")
        self.categories = categories

    def _run(
        self,
        conversation: str,
        available_categories: List[str],
        current_path: List[str] = None,
        level: int = 1,
        chat_history: List[Dict] = None
    ) -> tuple[str, List[Dict]]:
        """
        执行单级分类

        Returns:
            (分类结果, 更新后的对话历史)
        """
        current_path = current_path or []
        chat_history = chat_history or []
        max_retries = 3  # 默认重试3次

        available_set = set(available_categories)

        for attempt in range(max_retries):
            # 生成提示词（传入categories对象）
            prompt = ClassificationPrompts.create_prompt(
                conversation=conversation,
                available_categories=available_categories,
                current_path=current_path,
                level=level,
                categories=self.categories
            )

            # 构建消息列表：对话历史 + 当前提示
            messages = chat_history.copy()
            messages.append({"role": "user", "content": prompt})

            # 调用LLM
            result = self.llm_client.chat_completion(
                messages=messages,
                max_tokens=8192  # 默认最大token数
            )

            category = result.strip()
            logger.info(f"分类结果: {category}")

            # 清理【】符号（模型可能输出带括号的结果）
            category_cleaned = category.strip('【】')

            # 验证结果
            if category_cleaned in available_set:
                # 更新对话历史
                updated_history = messages.copy()
                updated_history.append({"role": "assistant", "content": category_cleaned})
                return category_cleaned, updated_history

            logger.warning(
                f"分类结果 '{category}' 不在可选项中，"
                f"正在重试 ({attempt + 1}/{max_retries})"
            )

        # 多次重试后使用默认值
        logger.warning(f"多次重试后仍未得到有效分类，使用第一个选项")
        fallback = available_categories[0]

        # 即使是fallback也要更新历史
        updated_history = messages.copy()
        updated_history.append({"role": "assistant", "content": fallback})
        return fallback, updated_history

    async def _arun(self, *args, **kwargs):
        """异步运行（暂不实现）"""
        raise NotImplementedError("异步模式暂未实现")
