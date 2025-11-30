"""
配置管理模块
基于Pydantic的配置管理，支持环境变量
"""
import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings(BaseModel):
    """全局配置"""

    # ============================================
    # API 配置
    # ============================================
    openai_api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_api_base: str = Field(
        default_factory=lambda: os.getenv(
            "OPENAI_API_BASE",
            "http://35.220.164.252:3888/v1"
        )
    )

    # ============================================
    # 模型配置
    # ============================================
    default_model: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_MODEL", "deepseek-chat")
    )
    default_temperature: float = Field(
        default_factory=lambda: float(os.getenv("DEFAULT_TEMPERATURE", "0"))
    )

    # Agent 模型
    agent_model: str = Field(
        default_factory=lambda: os.getenv("AGENT_MODEL", "deepseek-chat")
    )
    agent_temperature: float = Field(
        default_factory=lambda: float(os.getenv("AGENT_TEMPERATURE", "0"))
    )

    # ============================================
    # 数据路径
    # ============================================
    category_csv_path: str = Field(
        default_factory=lambda: os.getenv(
            "CATEGORY_CSV_PATH",
            "data/categories.csv"
        )
    )

    # ============================================
    # API服务配置
    # ============================================
    api_host: str = Field(
        default_factory=lambda: os.getenv("API_HOST", "0.0.0.0")
    )
    api_port: int = Field(
        default_factory=lambda: int(os.getenv("API_PORT", "8008"))
    )

    # ============================================
    # LangChain 配置
    # ============================================
    langchain_tracing_v2: bool = Field(
        default_factory=lambda: os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    )
    langchain_endpoint: str = Field(
        default_factory=lambda: os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    )
    langchain_api_key: str = Field(
        default_factory=lambda: os.getenv("LANGCHAIN_API_KEY", "")
    )
    langchain_project: str = Field(
        default_factory=lambda: os.getenv("LANGCHAIN_PROJECT", "summaryAndCategory")
    )

    # ============================================
    # 日志配置
    # ============================================
    log_level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )

    class Config:
        """Pydantic配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
