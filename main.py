"""
本地运行入口 - 无需FastAPI
直接在命令行运行对话分类和摘要
"""
import sys
from loguru import logger

from agent.orchestrator import ConversationAnalyzer
from models.schemas import ConversationRequest
from config.settings import settings

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level=settings.log_level
)


def analyze_conversation(conversation_text: str, conversation_id: str = "local", user_no: str = "user"):
    """
    分析对话并输出结果

    Args:
        conversation_text: 对话内容
        conversation_id: 会话ID（可选）
        user_no: 用户编号（可选）
    """
    # 初始化分析器
    logger.info("正在初始化对话分析器...")
    analyzer = ConversationAnalyzer()

    # 创建请求
    message_num = str(conversation_text.count('\n') + 1)
    request = ConversationRequest(
        conversationId=conversation_id,
        userNo=user_no,
        conversation=conversation_text,
        messageNum=message_num
    )

    # 执行分析
    logger.info("=" * 60)
    logger.info("开始分析对话")
    logger.info("=" * 60)

    result = analyzer.analyze(request)

    # 输出结果
    logger.info("=" * 60)
    logger.info("分析结果")
    logger.info("=" * 60)
    print(f"\n会话ID: {result.conversationId}")
    print(f"用户编号: {result.userNo}")
    print(f"分类: {result.category}")
    print(f"摘要: {result.summary}")
    print(f"状态: {result.message}")
    print()

    return result


def main():
    """主函数"""
    # 示例对话
    example_conversation = """客户：我想退飞享会员
客服：好的，请问您是什么原因想要退订呢？
客户：感觉不太用得上
客服：理解您的需求，我帮您办理退订"""

    logger.info("使用示例对话进行测试")
    logger.info("如需分析自定义对话，请修改此脚本中的 conversation_text 变量")
    logger.info("-" * 60)

    analyze_conversation(example_conversation)


if __name__ == "__main__":
    main()
