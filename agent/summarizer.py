"""
摘要生成Agent
"""
from loguru import logger
from tools.summarize import SummarizeTool


class SummarizerAgent:
    """摘要生成Agent"""

    def __init__(self):
        self.summarize_tool = SummarizeTool()
        logger.debug("摘要Agent初始化完成")

    def summarize(self, cleaned_conversation: str) -> str:
        """
        生成摘要

        Args:
            cleaned_conversation: 清洗后的对话

        Returns:
            摘要文本
        """
        logger.info("开始生成摘要...")
        summary = self.summarize_tool._run(conversation=cleaned_conversation)
        logger.success("摘要生成完成")
        return summary
