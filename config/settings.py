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
            "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    )

    # ============================================
    # 模型配置
    # ============================================
    default_model: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_MODEL", "qwen-max")
    )

    # 分类模型
    classification_model: str = Field(
        default_factory=lambda: os.getenv("CLASSIFICATION_MODEL", "qwen-max")
    )
    classification_temperature: float = Field(
        default_factory=lambda: float(os.getenv("CLASSIFICATION_TEMPERATURE", "0.01"))
    )
    classification_top_p: float = Field(
        default_factory=lambda: float(os.getenv("CLASSIFICATION_TOP_P", "0.8"))
    )
    classification_max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("CLASSIFICATION_MAX_TOKENS", "8192"))
    )
    classification_max_retries: int = Field(
        default_factory=lambda: int(os.getenv("CLASSIFICATION_MAX_RETRIES", "3"))
    )

    # 摘要模型
    summary_model: str = Field(
        default_factory=lambda: os.getenv("SUMMARY_MODEL", "qwen-max")
    )
    summary_temperature: float = Field(
        default_factory=lambda: float(os.getenv("SUMMARY_TEMPERATURE", "0.01"))
    )
    summary_top_p: float = Field(
        default_factory=lambda: float(os.getenv("SUMMARY_TOP_P", "0.8"))
    )
    summary_max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("SUMMARY_MAX_TOKENS", "8192"))
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
