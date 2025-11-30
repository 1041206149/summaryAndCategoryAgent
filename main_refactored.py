"""
FastAPI应用入口
简化版，核心逻辑移至Agent层
"""
import sys
from fastapi import FastAPI
import uvicorn
from loguru import logger

from agent.orchestrator import ConversationAnalyzer
from models.schemas import ConversationRequest, ConversationResponse
from config.settings import settings

# 配置日志
logger.remove()  # 移除默认处理器
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level=settings.log_level
)

# 初始化FastAPI
app = FastAPI(
    title="对话分析API",
    description="基于LangChain的三级分类与摘要系统",
    version="2.0.0"
)

# 初始化分析器（全局单例）
analyzer = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化分析器"""
    global analyzer
    logger.info("正在初始化对话分析器...")
    try:
        analyzer = ConversationAnalyzer()
        logger.success("对话分析器初始化成功")
    except Exception as e:
        logger.error(f"对话分析器初始化失败: {e}")
        raise


@app.post("/ai/analyze", response_model=ConversationResponse)
async def analyze_conversation(request: ConversationRequest):
    """对话分析接口"""
    return analyzer.analyze(request)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": 200,
        "response": {
            "status": "healthy"
        },
        "message": "success"
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "对话分析API",
        "version": "2.0.0",
        "description": "基于LangChain的三级分类与摘要系统"
    }


if __name__ == "__main__":
    logger.info("启动对话分析服务...")
    logger.info(f"Host: {settings.api_host}, Port: {settings.api_port}")
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )
