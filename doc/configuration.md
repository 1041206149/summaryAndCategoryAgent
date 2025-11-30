# 配置说明

## 环境变量

### 必需配置
```env
# API密钥
OPENAI_API_KEY=your_api_key

# API地址
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 可选配置
```env
# 模型
CLASSIFICATION_MODEL=qwen-max
SUMMARY_MODEL=qwen-max

# 分类参数
CLASSIFICATION_TEMPERATURE=0.01
CLASSIFICATION_MAX_RETRIES=3

# 摘要参数
SUMMARY_TEMPERATURE=0.01

# 服务配置
API_HOST=0.0.0.0
API_PORT=8008

# 日志级别
LOG_LEVEL=INFO
```

## 配置文件

### config/settings.py
所有配置的定义和默认值

### .env
本地环境变量（不提交到Git）

### .env.example
配置模板（提交到Git）

## 场景化配置

LLM客户端支持3种场景：

```python
# 分类场景
LLMClient.for_scenario("classification")

# 摘要场景
LLMClient.for_scenario("summary")

# 默认场景
LLMClient.for_scenario("default")
```

每种场景有独立的模型、温度等参数。
