# 对话分类与摘要系统 v2.0

基于LangChain重构的三级分类与摘要生成系统。

## 特点

- ✅ 6层模块化架构
- ✅ qwen-max云端模型
- ✅ LangChain工具集成
- ✅ 完整的类型验证
- ✅ 5/5测试通过

## 快速开始

```bash
# 1. 安装
pip install -r requirements.txt

# 2. 配置
cp .env.example .env
# 编辑.env填写API密钥

# 3. 测试
python test_refactored.py

# 4. 运行
python main_refactored.py
```

访问: http://localhost:8008/docs

## 文档

- [架构说明](doc/architecture.md)
- [快速开始](doc/quickstart.md)
- [API文档](doc/api.md)
- [配置说明](doc/configuration.md)
- [开发指南](doc/development.md)

详细文档见 `doc/` 目录。

## 目录结构

```
├── config/          # 配置管理
├── models/          # 数据模型
├── utils/           # LLM客户端
├── prompts/         # 提示词模板
├── tools/           # LangChain工具
├── agent/           # Agent层
├── data/            # 分类数据
├── doc/             # 文档
└── main_refactored.py
```

## API示例

```bash
curl -X POST "http://localhost:8008/ai/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "test",
    "userNo": "user",
    "conversation": "客户：我想退飞享会员\n客服：好的",
    "messageNum": "2"
  }'
```

## 技术栈

- FastAPI - Web框架
- LangChain - AI框架
- Pydantic - 数据验证
- qwen-max - LLM模型

## License

MIT
