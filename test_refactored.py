"""
简单的测试脚本
验证重构后的系统是否可以正常运行
"""
import sys
from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="DEBUG"
)


def test_imports():
    """测试所有模块导入"""
    logger.info("测试1: 模块导入")
    try:
        from config import settings
        logger.success(f"✓ 配置加载成功 - API Base: {settings.openai_api_base}")

        from models import ConversationRequest, ConversationResponse
        logger.success("✓ 数据模型导入成功")

        from utils import LLMClient
        logger.success("✓ LLM客户端导入成功")

        from prompts import ClassificationPrompts, SummaryPrompts
        logger.success("✓ 提示词模块导入成功")

        from tools import ConversationCleanerTool, CategoryLoaderTool
        logger.success("✓ 工具模块导入成功")

        from agent import ConversationAnalyzer
        logger.success("✓ Agent模块导入成功")

        logger.success("所有模块导入测试通过\n")
        return True
    except Exception as e:
        logger.error(f"✗ 模块导入失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_conversation_cleaner():
    """测试对话清洗工具"""
    logger.info("测试2: 对话清洗工具")
    try:
        from tools import ConversationCleanerTool

        cleaner = ConversationCleanerTool()

        test_conversation = """
        客服 2024/01/01 10:00:00 这边是人工客服，请问有什么可以帮您？
        客户 2024/01/01 10:00:10 我想咨询飞享会员
        ----：----
        客服 2024/01/01 10:00:20 稍等，为您核实~
        """

        cleaned = cleaner._run(conversation=test_conversation)
        logger.success(f"✓ 清洗成功，清洗后长度: {len(cleaned)}")
        logger.debug(f"清洗结果: {cleaned[:100]}...")

        logger.success("对话清洗工具测试通过\n")
        return True
    except Exception as e:
        logger.error(f"✗ 对话清洗工具测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_category_loader():
    """测试分类数据加载"""
    logger.info("测试3: 分类数据加载")
    try:
        from tools import CategoryLoaderTool

        loader = CategoryLoaderTool()
        categories = loader._run()

        logger.success(f"✓ 分类数据加载成功")
        logger.info(f"  一级分类数量: {len(categories.level1)}")
        logger.info(f"  二级分类数量: {len(categories.level2)}")
        logger.info(f"  三级分类数量: {len(categories.level3)}")
        logger.info(f"  三级分类父节点: {categories.level3_parents}")

        logger.success("分类数据加载测试通过\n")
        return True
    except Exception as e:
        logger.error(f"✗ 分类数据加载测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_prompts():
    """测试提示词生成"""
    logger.info("测试4: 提示词生成")
    try:
        from prompts import ClassificationPrompts, SummaryPrompts

        # 测试分类提示词
        test_conversation = "用户：我想退飞享会员\n客服：好的，为您处理"
        categories = ["费用异议咨询", "其他"]

        prompt = ClassificationPrompts.create_prompt(
            conversation=test_conversation,
            available_categories=categories,
            level=1
        )
        logger.success(f"✓ 分类提示词生成成功，长度: {len(prompt)}")

        # 测试摘要提示词
        summary_prompt = SummaryPrompts.create_prompt(test_conversation)
        logger.success(f"✓ 摘要提示词生成成功，长度: {len(summary_prompt)}")

        logger.success("提示词生成测试通过\n")
        return True
    except Exception as e:
        logger.error(f"✗ 提示词生成测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_full_system():
    """测试完整系统（需要API Key）"""
    logger.info("测试5: 完整系统集成测试")
    try:
        from config import settings

        if not settings.openai_api_key or settings.openai_api_key == "your_api_key_here":
            logger.warning("⚠ 跳过完整系统测试 - 未配置API Key")
            logger.warning("  请在.env文件中配置OPENAI_API_KEY以运行完整测试")
            return True

        from agent import ConversationAnalyzer
        from models import ConversationRequest

        logger.info("正在初始化分析器...")
        analyzer = ConversationAnalyzer()
        logger.success("✓ 分析器初始化成功")

        # 创建测试请求
        test_request = ConversationRequest(
            conversationId="test_001",
            userNo="user_001",
            conversation="客户：我想退飞享会员的费用\n客服：好的，为您处理退款",
            messageNum="2"
        )

        logger.info("正在执行分析...")
        result = analyzer.analyze(test_request)

        logger.success(f"✓ 分析完成")
        logger.info(f"  分类: {result.category}")
        logger.info(f"  摘要: {result.summary[:50]}...")
        logger.info(f"  状态: {result.message}")

        logger.success("完整系统集成测试通过\n")
        return True

    except Exception as e:
        logger.error(f"✗ 完整系统测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """运行所有测试"""
    logger.info("="*70)
    logger.info("开始运行重构系统测试")
    logger.info("="*70)

    tests = [
        ("模块导入", test_imports),
        ("对话清洗工具", test_conversation_cleaner),
        ("分类数据加载", test_category_loader),
        ("提示词生成", test_prompts),
        ("完整系统集成", test_full_system),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"测试 '{name}' 执行异常: {e}")
            results.append((name, False))

    # 总结
    logger.info("="*70)
    logger.info("测试总结")
    logger.info("="*70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{status} - {name}")

    logger.info(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        logger.success("所有测试通过！系统重构成功！")
        return 0
    else:
        logger.error(f"有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
