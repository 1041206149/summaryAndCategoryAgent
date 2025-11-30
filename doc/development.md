# 开发指南

## 添加新工具

1. 在 `tools/` 创建文件
2. 继承 `BaseTool`
3. 实现 `_run()` 方法
4. 在 `tools/__init__.py` 导出

示例：
```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    text: str = Field(description="输入文本")

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "工具描述"
    args_schema: type[BaseModel] = MyToolInput

    def _run(self, text: str) -> str:
        # 实现逻辑
        return result
```

## 修改提示词

编辑 `prompts/` 下的对应文件：
- `classification.py` - 分类提示词
- `summary.py` - 摘要提示词

## 调整配置

1. 在 `config/settings.py` 添加配置项
2. 在 `.env` 设置环境变量
3. 使用 `settings.xxx` 访问

## 运行测试

```bash
# 所有测试
python test_refactored.py

# 单个测试
python -c "from test_refactored import test_xxx; test_xxx()"
```

## 日志调试

```python
from loguru import logger

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

## Git工作流

```bash
# 创建功能分支
git checkout -b feature/xxx

# 提交代码
git add .
git commit -m "feat: 添加xxx功能"

# 推送并创建PR
git push -u origin feature/xxx
```
