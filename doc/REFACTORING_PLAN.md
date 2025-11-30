# 三级分类项目 LangChain 重构优化方案

## 项目概述

### 当前项目状态
- **项目名称**: summaryAndCategory (对话分类与摘要生成系统)
- **核心功能**:
  1. 对话清洗 (`chat_clean.py`)
  2. 三级分类 (层级化分类决策)
  3. 对话摘要生成
- **技术栈**: FastAPI + transformers (GLM-4-9B) + pandas
- **架构**: 单文件主程序 (summaryAndCategory.py)，辅助清洗模块

### 参考项目 (web2json-agent)
- **项目定位**: HTML解析代码生成Agent
- **技术栈**: LangChain 1.0 + OpenAI API + Playwright
- **架构特点**:
  - 清晰的分层架构 (agent/tools/prompts/config/utils)
  - LangChain工具链封装
  - 配置管理集中化
  - 良好的日志和错误处理

---

## 架构设计

### 1. 目标目录结构

```
summaryAndCategory/
├── main.py                          # FastAPI应用入口
├── config/
│   ├── __init__.py
│   └── settings.py                  # 配置管理 (基于pydantic)
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py             # 核心编排器 (分类+摘要)
│   ├── classifier.py               # 分类Agent
│   └── summarizer.py               # 摘要生成Agent
├── tools/
│   ├── __init__.py
│   ├── conversation_cleaner.py     # 对话清洗工具 (重构chat_clean)
│   ├── category_loader.py          # 分类数据加载工具
│   ├── classify_level.py           # 单级分类工具
│   └── summarize.py                # 摘要生成工具
├── prompts/
│   ├── __init__.py
│   ├── classification.py           # 分类提示词模板
│   └── summary.py                  # 摘要提示词模板
├── utils/
│   ├── __init__.py
│   └── llm_client.py               # LLM客户端封装 (支持本地/远程模型)
├── models/
│   ├── __init__.py
│   └── schemas.py                  # Pydantic数据模型
├── data/
│   └── 小结分类.csv                # 分类层级数据
├── tests/
│   ├── __init__.py
│   ├── test_cleaner.py
│   ├── test_classifier.py
│   └── test_summarizer.py
├── .env                            # 环境配置
├── requirements.txt                # 依赖管理
└── README.md                       # 项目文档
```

---

## 详细模块设计

### 2. 配置层 (config/)

#### 2.1 `config/settings.py`

```python
"""
配置管理模块
参考: web2json-agent/config/settings.py
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
    # 模型配置
    # ============================================
    # 本地模型路径 (GLM-4-9B)
    model_path: str = Field(
        default_factory=lambda: os.getenv(
            "MODEL_PATH",
            "/root/autodl-tmp/glm-4-9b-chat"
        )
    )
    device: str = Field(
        default_factory=lambda: os.getenv("DEVICE", "cuda")
    )

    # ============================================
    # 分类任务配置
    # ============================================
    classification_temperature: float = Field(
        default_factory=lambda: float(os.getenv("CLASSIFICATION_TEMPERATURE", "0.01"))
    )
    classification_top_p: float = Field(
        default_factory=lambda: float(os.getenv("CLASSIFICATION_TOP_P", "0.8"))
    )
    classification_max_length: int = Field(
        default_factory=lambda: int(os.getenv("CLASSIFICATION_MAX_LENGTH", "8192"))
    )
    classification_max_retries: int = Field(
        default_factory=lambda: int(os.getenv("CLASSIFICATION_MAX_RETRIES", "3"))
    )

    # ============================================
    # 摘要任务配置
    # ============================================
    summary_temperature: float = Field(
        default_factory=lambda: float(os.getenv("SUMMARY_TEMPERATURE", "0.01"))
    )
    summary_top_p: float = Field(
        default_factory=lambda: float(os.getenv("SUMMARY_TOP_P", "0.8"))
    )
    summary_max_length: int = Field(
        default_factory=lambda: int(os.getenv("SUMMARY_MAX_LENGTH", "8192"))
    )

    # ============================================
    # 数据路径
    # ============================================
    category_csv_path: str = Field(
        default_factory=lambda: os.getenv(
            "CATEGORY_CSV_PATH",
            "data/小结分类.csv"
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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
```

**优势**:
- 集中管理所有配置参数
- 通过 `.env` 文件灵活配置
- 类型安全 (pydantic验证)
- 便于单元测试 (可mock配置)

---

### 3. 数据模型层 (models/)

#### 3.1 `models/schemas.py`

```python
"""
数据模型定义
使用Pydantic进行数据验证
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ConversationRequest(BaseModel):
    """对话分析请求"""
    conversationId: str = Field(..., description="会话ID")
    userNo: str = Field(..., description="用户编号")
    conversation: str = Field(..., description="对话内容")
    messageNum: str = Field(..., description="消息数量")


class ConversationResponse(BaseModel):
    """对话分析响应"""
    conversationId: str
    userNo: str
    category: str = Field(default="", description="分类路径 (一级-二级-三级)")
    summary: str = Field(default="", description="对话摘要")
    message: str = Field(default="success", description="处理状态")


class CategoryNode(BaseModel):
    """分类节点"""
    id: int
    name: str
    parent_id: int
    level: int
    children: Dict[str, 'CategoryNode'] = Field(default_factory=dict)


class CategoryData(BaseModel):
    """分类数据结构"""
    level1: Dict[int, Dict] = Field(default_factory=dict)
    level2: Dict[str, Dict] = Field(default_factory=dict)
    level3: Dict[str, str] = Field(default_factory=dict)
    level3_parents: set = Field(default_factory=lambda: {'飞享会员', '提额卡', '新提额卡'})


class ClassificationResult(BaseModel):
    """分类结果"""
    level1: str
    level2: str
    level3: Optional[str] = None
    path: List[str] = Field(default_factory=list)

    @property
    def category_string(self) -> str:
        """返回分类路径字符串"""
        return "-".join(self.path)
```

**优势**:
- 清晰的数据结构定义
- 自动数据验证
- 便于API文档生成 (FastAPI集成)

---

### 4. 工具层 (tools/)

#### 4.1 `tools/conversation_cleaner.py`

```python
"""
对话清洗工具
将原 chat_clean.py 封装为 LangChain Tool
"""
import re
import pandas as pd
from typing import Dict, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class ConversationCleanerInput(BaseModel):
    """清洗工具输入"""
    conversation: str = Field(description="原始对话内容")


class ConversationCleanerTool(BaseTool):
    """对话清洗工具"""
    name: str = "conversation_cleaner"
    description: str = "清洗对话内容，去除敏感信息、无意义文本等"
    args_schema: type[BaseModel] = ConversationCleanerInput

    # 无意义短语列表
    meaningless_phrases: list = [
        "这边是人工客服，请问有什么可以帮您？",
        "您好，智能客服小飞为您服务！可以点击/:no选择下方问题或输入您的问题/:?",
        # ... 其他短语
    ]

    def _run(self, conversation: str) -> str:
        """执行清洗"""
        if pd.isna(conversation) or not isinstance(conversation, str):
            return ""

        # 按顺序应用所有清理函数
        text = self._remove_robot_messages(conversation)
        text = self._clean_basic_content(text)
        text = self._remove_sensitive_lines(text)
        text = self._mask_sensitive_info(text)
        text = self._remove_empty_lines(text)
        text = self._clean_messages(text)
        text = self._clean_customer_service_messages(text)
        text = self._concatenate_lines_with_colon(text)
        text = self._remove_sensitive_info_and_responses(text)
        text = self._remove_isolated_customer_lines(text)
        text = self._remove_empty_lines(text)

        # 最终清理
        text = re.sub(r'\s{2,}', ' ', text)
        text = text.replace("----：----", "")
        text = text.replace("-----以下是人工客服消息-----", "")

        return text.strip()

    def _clean_basic_content(self, text: str) -> str:
        """删除无意义文本"""
        for phrase in self.meaningless_phrases:
            text = text.replace(phrase, "")
        return text.strip()

    # ... 其他清洗方法保持不变
```

**优势**:
- 封装为 LangChain Tool，可与其他工具链式调用
- 输入/输出类型明确
- 便于测试和复用

#### 4.2 `tools/category_loader.py`

```python
"""
分类数据加载工具
"""
import pandas as pd
from pathlib import Path
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from models.schemas import CategoryData
from config.settings import settings
from loguru import logger


class CategoryLoaderTool(BaseTool):
    """分类数据加载工具"""
    name: str = "category_loader"
    description: str = "加载三级分类数据"

    def _run(self) -> CategoryData:
        """加载分类数据"""
        try:
            csv_path = Path(settings.category_csv_path)
            logger.info(f"正在读取分类文件: {csv_path}")

            df = pd.read_csv(csv_path)
            df = df[df['id'].astype(str).str.isnumeric()]

            df['id'] = df['id'].astype(int)
            df['parent_id'] = df['parent_id'].astype(int)
            df['level'] = df['level'].astype(int)

            categories = CategoryData()

            # 构建分类树
            for _, row in df.iterrows():
                cat_id = row['id']
                name = row['name']
                parent_id = row['parent_id']
                level = row['level']

                if level == 1:
                    categories.level1[cat_id] = {
                        'name': name,
                        'children': {}
                    }
                elif level == 2:
                    for l1_id, l1_info in categories.level1.items():
                        if parent_id == l1_id:
                            l1_info['children'][name] = []
                            categories.level2[name] = {
                                'parent': l1_info['name'],
                                'children': []
                            }
                            break
                elif level == 3:
                    for l2_name, l2_info in categories.level2.items():
                        parent_row = df[df['name'] == l2_name]
                        if not parent_row.empty and parent_row['id'].iloc[0] == parent_id:
                            categories.level2[l2_name]['children'].append(name)
                            categories.level3[name] = l2_name
                            break

            logger.success(f"分类数据加载完成")
            return categories

        except Exception as e:
            logger.error(f"加载分类数据失败: {str(e)}")
            raise
```

#### 4.3 `tools/classify_level.py`

```python
"""
单级分类工具
"""
from typing import List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from utils.llm_client import LLMClient
from prompts.classification import ClassificationPrompts
from config.settings import settings
from loguru import logger


class ClassifyLevelInput(BaseModel):
    """分类输入"""
    conversation: str = Field(description="清洗后的对话内容")
    available_categories: List[str] = Field(description="可选分类列表")
    current_path: List[str] = Field(default_factory=list, description="当前分类路径")
    level: int = Field(description="当前分类级别 (1/2/3)")


class ClassifyLevelTool(BaseTool):
    """单级分类工具"""
    name: str = "classify_level"
    description: str = "对对话进行单级分类决策"
    args_schema: type[BaseModel] = ClassifyLevelInput

    llm_client: LLMClient = None

    def __init__(self):
        super().__init__()
        # 初始化LLM客户端
        self.llm_client = LLMClient(
            model_path=settings.model_path,
            device=settings.device
        )

    def _run(
        self,
        conversation: str,
        available_categories: List[str],
        current_path: List[str] = None,
        level: int = 1
    ) -> str:
        """执行单级分类"""
        current_path = current_path or []
        max_retries = settings.classification_max_retries

        available_set = set(available_categories)

        for attempt in range(max_retries):
            # 生成提示词
            prompt = ClassificationPrompts.create_prompt(
                conversation=conversation,
                available_categories=available_categories,
                current_path=current_path,
                level=level
            )

            # 调用LLM
            result = self.llm_client.generate(
                prompt=prompt,
                temperature=settings.classification_temperature,
                top_p=settings.classification_top_p,
                max_length=settings.classification_max_length
            )

            category = result.strip()
            logger.info(f"分类结果: {category}")

            # 验证结果
            if category in available_set:
                return category

            logger.warning(
                f"分类结果 '{category}' 不在可选项中，"
                f"正在重试 ({attempt + 1}/{max_retries})"
            )

        # 多次重试后使用默认值
        logger.warning(f"多次重试后仍未得到有效分类，使用第一个选项")
        return available_categories[0]
```

#### 4.4 `tools/summarize.py`

```python
"""
摘要生成工具
"""
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from utils.llm_client import LLMClient
from prompts.summary import SummaryPrompts
from config.settings import settings


class SummarizeInput(BaseModel):
    """摘要输入"""
    conversation: str = Field(description="清洗后的对话内容")


class SummarizeTool(BaseTool):
    """摘要生成工具"""
    name: str = "summarize"
    description: str = "生成对话摘要"
    args_schema: type[BaseModel] = SummarizeInput

    llm_client: LLMClient = None

    def __init__(self):
        super().__init__()
        self.llm_client = LLMClient(
            model_path=settings.model_path,
            device=settings.device
        )

    def _run(self, conversation: str) -> str:
        """生成摘要"""
        prompt = SummaryPrompts.create_prompt(conversation)

        summary = self.llm_client.generate(
            prompt=prompt,
            temperature=settings.summary_temperature,
            top_p=settings.summary_top_p,
            max_length=settings.summary_max_length
        )

        return summary.strip()
```

---

### 5. 提示词层 (prompts/)

#### 5.1 `prompts/classification.py`

```python
"""
分类提示词模板
将硬编码的提示词抽离为独立模块
"""
from typing import List


class ClassificationPrompts:
    """分类提示词管理"""

    # 一级分类指南
    LEVEL1_GUIDE = {
        "APP下载和注册": "主要是注销账号、更换手机号",
        "额度激活咨询": "额度咨询、额度提升等（如果是提额卡相关问题请选择\"费用异议咨询\"分类）",
        "提现申请咨询": "提现、借款、放款相关问题",
        "贷款还款咨询": "还款相关问题，如：还款方式、还款失败、转账销账、还款时间、账单查询等",
        "费用异议咨询": "主要是一些退款、续费、权益等问题，例如飞享会员、提额卡、利息、担保费、逾期费等相关问题（这是最常用的分类）",
        "贷后凭证开具": "主要是查看和开具合同，还有结清证明、征信问题、发票等",
        "机票分期": "涉及机票业务（不常用分类）",
        "产品活动咨询": "涉及营销活动（不常用分类）",
        "催收相关业务": "涉及催收问题，如停催缓催、催收投诉、协商还款等",
        "其他": "不属于以上类别的问题"
    }

    @classmethod
    def create_prompt(
        cls,
        conversation: str,
        available_categories: List[str],
        current_path: List[str] = None,
        level: int = 1
    ) -> str:
        """
        创建分类提示词

        Args:
            conversation: 对话内容
            available_categories: 可选分类列表
            current_path: 当前分类路径
            level: 分类级别

        Returns:
            格式化的提示词
        """
        current_path = current_path or []
        level_names = {1: "一级", 2: "二级", 3: "三级"}

        if level == 1:
            # 一级分类提示词
            categories_str = "\n".join([
                f"● {cat}\n  └─ {cls.LEVEL1_GUIDE[cat]}"
                for cat in available_categories
            ])

            prompt = f"""作为专业的对话分类分析师，请对以下对话进行一级分类。请注意，一级分类是最重要的，它决定了后续的分类方向。

当前分类层级: 一级分类

当前对话内容:
{conversation}

可选的一级分类及其含义:
{categories_str}

分类规则：
1. 仔细阅读对话内容，准确判断主要诉求
2. 根据主要诉求选择最匹配的一级分类
3. 只输出分类名称，不要输出任何解释
4. 必须从上述选项中选择，不能创建新的分类
5. 如果对话内容涉及多个分类，选择最主要的诉求对应的分类
6. 如果实在无法确定具体类别，再选择"其他"类

请直接输出一个分类名称。"""
        else:
            # 二级/三级分类提示词
            categories_str = "\n".join([f"● {cat}" for cat in available_categories])
            current_path_str = " > ".join(current_path)

            prompt = f"""作为专业的对话分类分析师，请对以下对话进行{level_names[level]}分类。

当前分类路径: {current_path_str}

对话内容:
{conversation}

可选的{level_names[level]}分类:
{categories_str}

分类规则：
1. 只能从上述分类选项中选择一个
2. 只输出分类名称，不要输出任何解释
3. 确保输出的分类名称与选项完全一致

提示：
1. 如果二级分类为"飞享会员"，重点区分用户诉求是"取消扣款"还是"取消续费"，不要混淆！如果没出现"续费"字眼，一般认为是取消扣款或退款。

请直接输出一个分类名称。"""

        return prompt
```

**优势**:
- 提示词与代码逻辑分离
- 便于调优和版本管理
- 支持A/B测试不同提示词
- 可以添加提示词版本控制

#### 5.2 `prompts/summary.py`

```python
"""
摘要提示词模板
"""


class SummaryPrompts:
    """摘要提示词管理"""

    TEMPLATE = """作为一名专业的对话分析师，请分析以下客服对话记录，提取关键信息并按照以下格式输出结构化摘要:

【沟通内容】
提取用户反馈的主要问题和诉求要点，保持简洁明了。如涉及产品需明确指出(如飞享会员)。多个诉求分条呈现。

【方案详情】
列出针对每个诉求的具体解决方案；如果有如下信息则需要注明，没有则忽略（仅给出解决方案）:
- 若涉及金额要明确标注具体数字
- 如果有减免、退款等操作要清晰说明
- 如果有订单编号则要说明

【处理结果】
说明最终处理状态，包括:
- 用户是否接受方案
- 相关操作是否已完成
- 如有待跟进事项需注明（没有则忽略这条）

要求:
1. 保持客观中立的叙述语气
2. 方案和金额必须准确对应原文
3. 按照【】分类标题组织内容
4. 多个问题按时间顺序分别完整描述
5. 每个部分表述要简明扼要
6. 总字数不要超过120字

请基于以上要求，分析如下对话内容:
{conversation}"""

    @classmethod
    def create_prompt(cls, conversation: str) -> str:
        """创建摘要提示词"""
        return cls.TEMPLATE.format(conversation=conversation)
```

---

### 6. LLM客户端层 (utils/)

#### 6.1 `utils/llm_client.py`

```python
"""
LLM客户端封装
支持本地模型 (GLM) 和远程API
参考: web2json-agent/utils/llm_client.py
"""
import torch
from threading import Thread
from typing import Optional
from transformers import (
    AutoTokenizer,
    AutoModel,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer
)
from loguru import logger


class StopOnTokens(StoppingCriteria):
    """停止标准"""
    def __init__(self, model):
        self.model = model

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = self.model.config.eos_token_id
        for stop_id in stop_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False


class LLMClient:
    """
    LLM客户端封装
    支持本地GLM模型
    """

    def __init__(
        self,
        model_path: str,
        device: str = "cuda"
    ):
        """
        初始化LLM客户端

        Args:
            model_path: 模型路径
            device: 设备 (cuda/cpu)
        """
        self.model_path = model_path
        self.device = device

        logger.info("正在加载模型和分词器...")

        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            encode_special_tokens=True
        )

        # 加载模型
        self.model = AutoModel.from_pretrained(
            model_path,
            trust_remote_code=True,
            device_map="auto"
        ).eval()

        logger.success(f"模型加载完成 - 设备: {device}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.01,
        top_p: float = 0.8,
        max_length: int = 8192
    ) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            temperature: 温度
            top_p: Top-p采样
            max_length: 最大长度

        Returns:
            生成的文本
        """
        logger.debug(f"开始生成 - 提示词长度: {len(prompt)}")

        messages = [{"role": "user", "content": prompt}]

        # 应用对话模板
        model_inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt"
        ).to(self.model.device)

        # 初始化流式输出
        streamer = TextIteratorStreamer(
            tokenizer=self.tokenizer,
            timeout=60,
            skip_prompt=True,
            skip_special_tokens=True
        )

        stop = StopOnTokens(self.model)

        # 生成参数
        generate_kwargs = {
            "input_ids": model_inputs,
            "streamer": streamer,
            "max_new_tokens": max_length,
            "do_sample": True,
            "top_p": top_p,
            "temperature": temperature,
            "stopping_criteria": StoppingCriteriaList([stop]),
            "repetition_penalty": 1.2,
            "eos_token_id": self.model.config.eos_token_id,
        }

        result = [""]

        def generate_and_store():
            try:
                self.model.generate(**generate_kwargs)
                logger.debug("模型生成完成")
            except Exception as e:
                logger.error(f"模型生成出错: {str(e)}")

        # 启动生成线程
        t = Thread(target=generate_and_store)
        t.start()

        # 收集生成文本
        for new_token in streamer:
            if new_token:
                result[0] += new_token

        t.join()

        return result[0].strip()
```

**优势**:
- 统一的LLM接口
- 支持扩展到远程API (OpenAI/Claude等)
- 便于切换不同模型
- 集成日志记录

---

### 7. Agent层 (agent/)

#### 7.1 `agent/classifier.py`

```python
"""
分类Agent
负责执行三级分类逻辑
"""
from typing import List
from loguru import logger
from tools.classify_level import ClassifyLevelTool
from models.schemas import CategoryData, ClassificationResult


class ClassificationAgent:
    """分类Agent"""

    def __init__(self, categories: CategoryData):
        """
        初始化分类Agent

        Args:
            categories: 分类数据
        """
        self.categories = categories
        self.classify_tool = ClassifyLevelTool()

    def classify(self, cleaned_conversation: str) -> ClassificationResult:
        """
        执行三级分类

        Args:
            cleaned_conversation: 清洗后的对话

        Returns:
            分类结果
        """
        logger.info("开始分层分类...")
        classification_path = []

        # 一级分类
        level1_categories = self._get_level1_categories()
        level1 = self.classify_tool._run(
            conversation=cleaned_conversation,
            available_categories=level1_categories,
            current_path=[],
            level=1
        )
        classification_path.append(level1)
        logger.info(f"一级分类: {level1}")

        # 二级分类
        level2_categories = self._get_level2_categories(level1)
        level2 = self.classify_tool._run(
            conversation=cleaned_conversation,
            available_categories=level2_categories,
            current_path=classification_path,
            level=2
        )
        classification_path.append(level2)
        logger.info(f"二级分类: {level2}")

        # 三级分类 (如果需要)
        level3 = None
        if level2 in self.categories.level3_parents:
            level3_categories = self._get_level3_categories(level2)
            level3 = self.classify_tool._run(
                conversation=cleaned_conversation,
                available_categories=level3_categories,
                current_path=classification_path,
                level=3
            )
            classification_path.append(level3)
            logger.info(f"三级分类: {level3}")

        logger.success(f"分类完成: {classification_path}")

        return ClassificationResult(
            level1=level1,
            level2=level2,
            level3=level3,
            path=classification_path
        )

    def _get_level1_categories(self) -> List[str]:
        """获取一级分类列表"""
        return [info['name'] for _, info in self.categories.level1.items()]

    def _get_level2_categories(self, level1: str) -> List[str]:
        """获取二级分类列表"""
        for l1_id, l1_info in self.categories.level1.items():
            if l1_info['name'] == level1:
                return list(l1_info['children'].keys())
        return []

    def _get_level3_categories(self, level2: str) -> List[str]:
        """获取三级分类列表"""
        if level2 in self.categories.level2:
            return self.categories.level2[level2]['children']
        return []
```

#### 7.2 `agent/summarizer.py`

```python
"""
摘要生成Agent
"""
from loguru import logger
from tools.summarize import SummarizeTool


class SummarizerAgent:
    """摘要生成Agent"""

    def __init__(self):
        self.summarize_tool = SummarizeTool()

    def summarize(self, cleaned_conversation: str) -> str:
        """
        生成摘要

        Args:
            cleaned_conversation: 清洗后的对话

        Returns:
            摘要文本
        """
        logger.info("开始生成摘要...")
        summary = self.summarize_tool._run(conversation=cleaned_conversation)
        logger.success("摘要生成完成")
        return summary
```

#### 7.3 `agent/orchestrator.py`

```python
"""
核心编排器
协调分类和摘要Agent
参考: web2json-agent/agent/orchestrator.py
"""
from loguru import logger
from tools.conversation_cleaner import ConversationCleanerTool
from tools.category_loader import CategoryLoaderTool
from agent.classifier import ClassificationAgent
from agent.summarizer import SummarizerAgent
from models.schemas import ConversationRequest, ConversationResponse


class ConversationAnalyzer:
    """
    对话分析编排器
    协调清洗、分类、摘要三个步骤
    """

    def __init__(self):
        """初始化编排器"""
        logger.info("初始化对话分析器...")

        # 初始化工具
        self.cleaner_tool = ConversationCleanerTool()
        self.category_loader = CategoryLoaderTool()

        # 加载分类数据
        self.categories = self.category_loader._run()

        # 初始化Agent
        self.classifier = ClassificationAgent(self.categories)
        self.summarizer = SummarizerAgent()

        logger.success("对话分析器初始化完成")

    def analyze(self, request: ConversationRequest) -> ConversationResponse:
        """
        分析对话

        Args:
            request: 分析请求

        Returns:
            分析结果
        """
        try:
            logger.info(f"开始分析会话: {request.conversationId}")

            # 步骤1: 清洗对话
            logger.info("[步骤 1/3] 清洗对话...")
            cleaned_conversation = self.cleaner_tool._run(
                conversation=request.conversation
            )
            logger.debug(f"清洗后内容: {cleaned_conversation[:200]}...")

            # 步骤2: 分类
            logger.info("[步骤 2/3] 执行分类...")
            classification_result = self.classifier.classify(cleaned_conversation)

            # 步骤3: 生成摘要
            logger.info("[步骤 3/3] 生成摘要...")
            summary = self.summarizer.summarize(cleaned_conversation)

            logger.success(f"分析完成 - 分类: {classification_result.category_string}")

            return ConversationResponse(
                conversationId=request.conversationId,
                userNo=request.userNo,
                category=classification_result.category_string,
                summary=summary,
                message="success"
            )

        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            return ConversationResponse(
                conversationId=request.conversationId,
                userNo=request.userNo,
                category="",
                summary="",
                message="fail"
            )
```

**优势**:
- 清晰的责任分离 (清洗/分类/摘要)
- 统一的错误处理
- 便于添加新功能 (如日志记录、监控)
- 符合单一职责原则

---

### 8. API入口 (main.py)

```python
"""
FastAPI应用入口
简化版，核心逻辑移至Agent层
"""
from fastapi import FastAPI
import uvicorn
from loguru import logger

from agent.orchestrator import ConversationAnalyzer
from models.schemas import ConversationRequest, ConversationResponse
from config.settings import settings

# 初始化FastAPI
app = FastAPI(
    title="对话分析API",
    description="基于GLM的三级分类与摘要系统",
    version="2.0.0"
)

# 初始化分析器
analyzer = ConversationAnalyzer()


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


if __name__ == "__main__":
    logger.info("启动对话分析服务...")
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )
```

**优势**:
- main.py 极简，只负责API路由
- 所有业务逻辑在Agent层
- 便于单元测试 (可直接测试analyzer)

---

## 重构优势总结

### 1. 架构优势
- **分层清晰**: config/models/tools/prompts/agent/api 各司其职
- **解耦合**: 提示词、配置、业务逻辑分离
- **可测试**: 每个模块可独立测试
- **可扩展**: 易于添加新工具、新分类级别

### 2. 代码质量提升
- **类型安全**: 使用Pydantic进行数据验证
- **错误处理**: 统一的异常处理和日志记录
- **可维护**: 代码结构清晰，便于理解和修改

### 3. LangChain集成
- **工具链化**: 所有组件封装为LangChain Tools
- **可组合**: 工具可灵活组合和复用
- **标准化**: 遵循LangChain最佳实践

### 4. 配置管理
- **集中化**: 所有配置在settings.py统一管理
- **环境分离**: 通过.env文件管理不同环境
- **类型安全**: Pydantic验证配置有效性

---

## 重构步骤建议

### 阶段1: 基础重构 (不改变功能)
1. 创建目录结构
2. 重构配置层 (config/)
3. 重构数据模型 (models/)
4. 重构LLM客户端 (utils/)

### 阶段2: 工具层重构
1. 重构对话清洗工具
2. 重构分类数据加载
3. 重构单级分类工具
4. 重构摘要生成工具

### 阶段3: Agent层重构
1. 实现分类Agent
2. 实现摘要Agent
3. 实现编排器

### 阶段4: API层重构
1. 简化main.py
2. 集成新的Agent层
3. 测试和验证

### 阶段5: 测试和优化
1. 编写单元测试
2. 性能测试
3. 日志和监控优化

---

## 依赖更新

### requirements.txt

```txt
# 现有依赖
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pandas==2.1.3
torch==2.1.0
transformers==4.35.0

# 新增依赖
langchain==0.1.0
langchain-core==0.1.0
python-dotenv==1.0.0
loguru==0.7.2
tiktoken==0.5.1
```

---

## 迁移风险和注意事项

### 1. 保持向后兼容
- API接口保持不变
- 数据模型保持一致
- 确保输出格式相同

### 2. 性能考虑
- LangChain封装可能带来轻微性能开销
- 需要进行性能测试对比
- 可通过配置调整优化

### 3. 测试覆盖
- 编写完整的单元测试
- 集成测试验证端到端流程
- 回归测试确保功能一致

### 4. 渐进式迁移
- 建议先在开发环境测试
- 可以保留旧版本作为备份
- 逐步迁移，而非一次性重写

---

## 后续优化方向

### 1. 功能增强
- 添加分类置信度评分
- 支持多轮对话追踪
- 实现分类结果缓存

### 2. 性能优化
- 批量处理优化
- 模型推理加速
- 异步处理支持

### 3. 监控和可观测性
- 添加Prometheus指标
- 集成分布式追踪
- 添加性能分析工具

### 4. 模型优化
- 提示词工程优化
- Few-shot学习支持
- 支持模型热更新

---

## 总结

本重构方案参考了web2json-agent的优秀架构设计，将现有的三级分类项目进行了全面的模块化和工程化改造。主要优势包括：

1. **清晰的分层架构**: 配置/模型/工具/提示词/Agent/API各层职责明确
2. **LangChain集成**: 利用LangChain工具链提升代码可组合性
3. **可维护性提升**: 代码结构清晰，便于测试和扩展
4. **配置管理优化**: 集中化配置，支持环境分离
5. **日志和错误处理**: 统一的日志记录和异常处理

重构后的项目将更易于维护、扩展和测试，为后续功能迭代打下坚实基础。
