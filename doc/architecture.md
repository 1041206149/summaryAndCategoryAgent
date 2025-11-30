# 项目架构

## 目录结构

```
summaryAndCategory/
├── config/              # 配置管理
├── models/              # 数据模型
├── utils/               # 工具库 (LLM客户端)
├── prompts/             # 提示词模板
├── tools/               # LangChain工具
├── agent/               # Agent层
├── data/                # 分类数据
├── main_refactored.py   # API入口
└── test_refactored.py   # 测试脚本
```

## 架构图

```
FastAPI
  ↓
ConversationAnalyzer (编排器)
  ↓
┌─────────┬─────────┬─────────┐
│ Cleaner │Classifier│Summarizer│ (Agent层)
└─────────┴─────────┴─────────┘
  ↓
┌─────────┬─────────┬─────────┐
│ Cleaner │Classify │Summarize│ (Tools层)
│  Tool   │  Tool   │  Tool   │
└─────────┴─────────┴─────────┘
  ↓
LLMClient (qwen-max)
```

## 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 配置 | `config/settings.py` | 环境变量配置 |
| 模型 | `models/schemas.py` | 数据验证 |
| 客户端 | `utils/llm_client.py` | qwen-max调用 |
| 提示词 | `prompts/*.py` | 分类/摘要模板 |
| 工具 | `tools/*.py` | 清洗/分类/摘要 |
| Agent | `agent/*.py` | 业务编排 |

## 数据流

```
请求 → 清洗 → 一级分类 → 二级分类 → 三级分类 → 摘要 → 响应
```
