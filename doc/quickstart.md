# 快速启动指南

## 1. 环境准备

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境变量
```bash
# 复制环境配置示例
cp .env.example .env

# 编辑.env文件，填写以下必需配置
vim .env
```

在`.env`文件中，至少需要配置：
```env
# API密钥（必需）
OPENAI_API_KEY=your_qwen_api_key_here

# API地址（必需）
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# 模型名称（可选，默认qwen-max）
CLASSIFICATION_MODEL=qwen-max
SUMMARY_MODEL=qwen-max
```

## 2. 测试系统

运行测试脚本验证系统：
```bash
python test_refactored.py
```

预期输出：
```
✓ 通过 - 模块导入
✓ 通过 - 对话清洗工具
✓ 通过 - 分类数据加载
✓ 通过 - 提示词生成
✓ 通过 - 完整系统集成

总计: 5/5 测试通过
所有测试通过！系统重构成功！
```

## 3. 启动服务

### 方式1: 直接运行
```bash
python main_refactored.py
```

### 方式2: 使用uvicorn（推荐生产环境）
```bash
uvicorn main_refactored:app --host 0.0.0.0 --port 8008 --reload
```

服务启动后，访问：
- API文档: http://localhost:8008/docs
- 健康检查: http://localhost:8008/health

## 4. API调用示例

### 使用curl
```bash
curl -X POST "http://localhost:8008/ai/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "test_001",
    "userNo": "user_001",
    "conversation": "客户：我想退飞享会员的费用\n客服：好的，为您处理退款",
    "messageNum": "2"
  }'
```

### 使用Python requests
```python
import requests

response = requests.post(
    "http://localhost:8008/ai/analyze",
    json={
        "conversationId": "test_001",
        "userNo": "user_001",
        "conversation": "客户：我想退飞享会员的费用\n客服：好的，为您处理退款",
        "messageNum": "2"
    }
)

result = response.json()
print(f"分类: {result['category']}")
print(f"摘要: {result['summary']}")
```

## 5. 目录结构说明

```
summaryAndCategory/
├── config/              # 配置管理
│   └── settings.py      # 所有配置参数
├── models/              # 数据模型
│   └── schemas.py       # Pydantic模型定义
├── utils/               # 工具函数
│   └── llm_client.py    # LLM客户端封装
├── prompts/             # 提示词模板
│   ├── classification.py
│   └── summary.py
├── tools/               # LangChain工具
│   ├── conversation_cleaner.py
│   ├── category_loader.py
│   ├── classify_level.py
│   └── summarize.py
├── agent/               # Agent逻辑
│   ├── classifier.py
│   ├── summarizer.py
│   └── orchestrator.py
├── data/                # 数据文件
│   └── 小结分类.csv
└── main_refactored.py   # API入口
```

## 6. 常见问题

### Q1: 模块导入错误
**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决**: 确保已安装所有依赖
```bash
pip install -r requirements.txt
```

### Q2: API密钥错误
**问题**: API调用失败

**解决**:
1. 检查`.env`文件中的`OPENAI_API_KEY`是否正确
2. 确认API地址`OPENAI_API_BASE`正确

### Q3: 分类数据加载失败
**问题**: `FileNotFoundError: data/小结分类.csv`

**解决**: 确保CSV文件在正确位置
```bash
ls data/小结分类.csv
```

### Q4: Token统计不可用
**问题**: 警告信息 `Tokenizer初始化失败`

**解决**: 这是正常的，不影响核心功能。如需token统计，确保网络连接正常。

## 7. 开发建议

### 修改分类提示词
编辑 `prompts/classification.py`:
```python
class ClassificationPrompts:
    LEVEL1_GUIDE = {
        # 修改这里的分类指南
    }
```

### 修改摘要格式
编辑 `prompts/summary.py`:
```python
class SummaryPrompts:
    TEMPLATE = """
    # 修改这里的摘要模板
    """
```

### 调整模型参数
编辑 `.env`:
```env
CLASSIFICATION_TEMPERATURE=0.01   # 分类温度
SUMMARY_TEMPERATURE=0.01          # 摘要温度
CLASSIFICATION_MAX_RETRIES=3      # 分类重试次数
```

## 8. 性能优化建议

### 1. 启用缓存
可以添加Redis缓存常见对话的分类结果

### 2. 批量处理
修改API支持批量请求处理

### 3. 异步处理
使用FastAPI的异步特性处理并发请求

## 9. 监控和日志

### 查看日志
日志输出到stdout，可以重定向到文件：
```bash
python main_refactored.py > app.log 2>&1
```

### 调整日志级别
在`.env`中设置：
```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 10. 部署建议

### 使用Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main_refactored.py"]
```

### 使用systemd (Linux)
创建服务文件 `/etc/systemd/system/summary-api.service`:
```ini
[Unit]
Description=Summary and Category API
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/summaryAndCategory
ExecStart=/usr/bin/python3 main_refactored.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start summary-api
sudo systemctl enable summary-api
```

## 需要帮助？

- 查看完整文档: `README.md`
- 查看重构方案: `REFACTORING_PLAN.md`
- 查看重构总结: `REFACTORING_SUMMARY.md`
- 运行测试: `python test_refactored.py`
