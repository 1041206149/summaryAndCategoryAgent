"""
核心编排器
协调分类和摘要Agent
参考: web2json-agent/agent/orchestrator.py
"""
from loguru import logger
from tools.conversation_cleaner import ConversationCleanerTool
from tools.category_loader import CategoryLoaderTool
from agent.classifier import ClassificationAgent
from agent.summarizer import SummarizerAgent
from models.schemas import ConversationRequest, ConversationResponse


class ConversationAnalyzer:
    """
    对话分析编排器
    协调清洗、分类、摘要三个步骤
    """

    def __init__(self):
        """初始化编排器"""
        logger.info("初始化对话分析器...")

        # 初始化工具
        self.cleaner_tool = ConversationCleanerTool()
        self.category_loader = CategoryLoaderTool()

        # 加载分类数据
        logger.info("加载分类数据...")
        self.categories = self.category_loader._run()

        # 初始化Agent
        self.classifier = ClassificationAgent(self.categories)
        self.summarizer = SummarizerAgent()

        logger.success("对话分析器初始化完成")

    def analyze(self, request: ConversationRequest) -> ConversationResponse:
        """
        分析对话

        Args:
            request: 分析请求

        Returns:
            分析结果
        """
        try:
            logger.info(f"开始分析会话: {request.conversationId}")

            # 步骤1: 清洗对话
            logger.info("[步骤 1/3] 清洗对话...")
            cleaned_conversation = self.cleaner_tool._run(
                conversation=request.conversation
            )
            logger.debug(f"清洗后内容长度: {len(cleaned_conversation)}")

            # 步骤2: 分类
            logger.info("[步骤 2/3] 执行分类...")
            classification_result = self.classifier.classify(cleaned_conversation)

            # 步骤3: 生成摘要
            logger.info("[步骤 3/3] 生成摘要...")
            summary = self.summarizer.summarize(cleaned_conversation)

            logger.success(f"分析完成 - 分类: {classification_result.category_string}")

            return ConversationResponse(
                conversationId=request.conversationId,
                userNo=request.userNo,
                category=classification_result.category_string,
                summary=summary,
                message="success"
            )

        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return ConversationResponse(
                conversationId=request.conversationId,
                userNo=request.userNo,
                category="",
                summary="",
                message="fail"
            )
