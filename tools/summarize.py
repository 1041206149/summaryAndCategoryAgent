"""
摘要生成工具
"""
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from utils.llm_client import LLMClient
from prompts.summary import SummaryPrompts
from config.settings import settings
from loguru import logger


class SummarizeInput(BaseModel):
    """摘要输入"""
    conversation: str = Field(description="清洗后的对话内容")


class SummarizeTool(BaseTool):
    """摘要生成工具"""
    name: str = "summarize"
    description: str = "生成对话摘要"
    args_schema: type[BaseModel] = SummarizeInput

    llm_client: LLMClient = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化LLM客户端（使用摘要场景配置）
        self.llm_client = LLMClient.for_scenario("summary")

    def _run(self, conversation: str) -> str:
        """生成摘要"""
        logger.debug("开始生成摘要")
        prompt = SummaryPrompts.create_prompt(conversation)

        messages = [{"role": "user", "content": prompt}]
        summary = self.llm_client.chat_completion(
            messages=messages,
            max_tokens=settings.summary_max_tokens
        )

        logger.debug("摘要生成完成")
        return summary.strip()

    async def _arun(self, *args, **kwargs):
        """异步运行（暂不实现）"""
        raise NotImplementedError("异步模式暂未实现")
