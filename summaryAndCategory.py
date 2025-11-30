from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import torch
from threading import Thread
from transformers import (
    AutoTokenizer,
    AutoModel,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer
)
import json
import pandas as pd
from typing import List, Optional, Dict
from chat_clean import ConversationCleaner  # 导入清洗模块
import uvicorn

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# 模型配置
MODEL_PATH = os.environ.get('MODEL_PATH', '/root/autodl-tmp/glm-4-9b-chat')
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

app = FastAPI(
    title="Text Analysis API",
    description="基于GLM的对话分析系统API",
    version="1.0.0"
)

# 初始化清洗器
cleaner = ConversationCleaner()


# 请求和响应模型定义
class ConversationRequest(BaseModel):
    conversationId: str
    userNo: str
    conversation: str
    messageNum: str


class ConversationResponse(BaseModel):
    conversationId: str
    userNo: str
    category: str = ""
    summary: str = ""
    message: str = "success"


class StopOnTokens(StoppingCriteria):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = model.config.eos_token_id
        for stop_id in stop_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False


# 加载模型和分词器
print("正在加载模型和分词器...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True,
    encode_special_tokens=True
)

model = AutoModel.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True,
    device_map="auto"
).eval()


def chat_with_model(prompt, temperature=0.01, top_p=0.8, max_length=8192):
    print("开始调用模型...")
    print(f"提示词长度: {len(prompt)} 字符")
    messages = [{"role": "user", "content": prompt}]

    
    model_inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_tensors="pt"
    ).to(model.device)
    

    print("初始化流式输出...")
    streamer = TextIteratorStreamer(
        tokenizer=tokenizer,
        timeout=60,
        skip_prompt=True,
        skip_special_tokens=True
    )

    stop = StopOnTokens()

    # 在这里定义 generate_kwargs
    generate_kwargs = {
        "input_ids": model_inputs,
        "streamer": streamer,
        "max_new_tokens": max_length,
        "do_sample": True,
        "top_p": top_p,
        "temperature": temperature,
        "stopping_criteria": StoppingCriteriaList([stop]),
        "repetition_penalty": 1.2,
        "eos_token_id": model.config.eos_token_id,
    }

    result = [""]
    print("开始生成回答...")

    def generate_and_store():
        try:
            model.generate(**generate_kwargs)
            print("模型生成完成")
        except Exception as e:
            print(f"模型生成过程中出错: {str(e)}")

    t = Thread(target=generate_and_store)
    t.start()

    print("正在收集生成的文本...")
    for new_token in streamer:
        if new_token:
            result[0] += new_token
    
    t.join()
    print("生成过程结束")
    return result[0].strip()

def load_category_data():
    try:
        csv_path = os.path.join(SCRIPT_DIR, '小结分类.csv')
        print(f"正在读取分类文件: {csv_path}")

        df = pd.read_csv(csv_path)
        df = df[df['id'].astype(str).str.isnumeric()]

        df['id'] = df['id'].astype(int)
        df['parent_id'] = df['parent_id'].astype(int)
        df['level'] = df['level'].astype(int)

        categories = {
            'level1': {},
            'level2': {},
            'level3': {},
            'level3_parents': set(['飞享会员', '提额卡', '新提额卡'])
        }

        for _, row in df.iterrows():
            cat_id = row['id']
            name = row['name']
            parent_id = row['parent_id']
            level = row['level']

            if level == 1:
                categories['level1'][cat_id] = {
                    'name': name,
                    'children': {}
                }
            elif level == 2:
                for l1_id, l1_info in categories['level1'].items():
                    if parent_id == l1_id:
                        l1_info['children'][name] = []
                        categories['level2'][name] = {
                            'parent': l1_info['name'],
                            'children': []
                        }
                        break
            elif level == 3:
                for l2_name, l2_info in categories['level2'].items():
                    parent_row = df[df['name'] == l2_name]
                    if not parent_row.empty and parent_row['id'].iloc[0] == parent_id:
                        categories['level2'][l2_name]['children'].append(name)
                        categories['level3'][name] = l2_name
                        break
        print(f"读取成功")
        print(categories)
        return categories
    except Exception as e:
        print(f"加载分类数据失败: {str(e)}")
        return None


def get_next_level_categories(categories, current_path=None):
    if not current_path:
        return [info['name'] for _, info in categories['level1'].items()]

    if len(current_path) == 1:
        for l1_id, l1_info in categories['level1'].items():
            if l1_info['name'] == current_path[0]:
                return list(l1_info['children'].keys())

    if len(current_path) == 2:
        if current_path[1] in categories['level3_parents']:
            return categories['level2'][current_path[1]]['children']

    return []


def create_classification_prompt(conversation, categories, current_path=None):
    current_level = len(current_path) + 1 if current_path else 1
    level_names = {1: "一级", 2: "二级", 3: "三级"}

    available_categories = get_next_level_categories(categories, current_path)

    level1_guide = {
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

    if current_level == 1:
        categories_str = "\n".join([f"● {cat}\n  └─ {level1_guide[cat]}" for cat in available_categories])

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
        categories_str = "\n".join([f"● {cat}" for cat in available_categories])
        current_path_str = " > ".join(current_path) if current_path else "开始分类"

        prompt = f"""作为专业的对话分类分析师，请对以下对话进行{level_names[current_level]}分类。

当前分类路径: {current_path_str}

对话内容:
{conversation}

可选的{level_names[current_level]}分类:
{categories_str}

分类规则：
1. 只能从上述分类选项中选择一个
2. 只输出分类名称，不要输出任何解释
3. 确保输出的分类名称与选项完全一致

提示：
1. 如果二级分类为"飞享会员"，重点区分用户诉求是"取消扣款"还是"取消续费"，不要混淆！如果没出现"续费"字眼，一般认为是取消扣款或退款。

请直接输出一个分类名称。"""

    return prompt


def verify_and_classify(conversation, categories, current_path, max_retries=3):

    available_categories = get_next_level_categories(categories, current_path)
    available_categories_set = set(available_categories)

    for attempt in range(max_retries):
        prompt = create_classification_prompt(conversation, categories, current_path)
        result = chat_with_model(prompt, temperature=0.01)
        category = result.strip()
        print(f"得到分类结果: {category}")
        if category in available_categories_set:
            return category

        print(f"警告：分类结果 '{category}' 不在可选项中，正在重试 ({attempt + 1}/{max_retries})")

    print(f"警告：多次重试后仍未得到有效的分类结果，使用第一个选项作为默认值")
    return available_categories[0]


def classify_conversation_hierarchical(conversation, categories):
    print("开始分层分类...")
    classification_path = []

    level1_category = verify_and_classify(conversation, categories, classification_path)
    classification_path.append(level1_category)
    print(f"一级分类结果: {level1_category}")

    level2_category = verify_and_classify(conversation, categories, classification_path)
    classification_path.append(level2_category)
    print(f"二级分类结果: {level2_category}")

    if level2_category in categories['level3_parents']:
        level3_category = verify_and_classify(conversation, categories, classification_path)
        classification_path.append(level3_category)
        print(f"三级分类结果: {level3_category}")

    print(f"分类完成，完整分类路径: {classification_path}")
    return classification_path


def create_summary_prompt(conversation):
    prompt_template = """作为一名专业的对话分析师，请分析以下客服对话记录，提取关键信息并按照以下格式输出结构化摘要:

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

    return prompt_template.format(conversation=conversation)


@app.post("/ai/analyze")
async def analyze_conversation(request: ConversationRequest):
    try:
        print("开始处理对话分析请求...")
        print(f"收到会话ID: {request.conversationId}")
        
        # 执行分类
        print("正在加载分类数据...")
        categories = load_category_data()
        if categories is None:
            print("分类系统初始化失败！")
            raise HTTPException(status_code=500, detail="分类系统初始化失败")

        # 清洗对话数据
        print("开始清洗对话数据...")
        cleaned_conversation = cleaner.clean_conversation(request.conversation)
        print("清洗后的对话内容:", cleaned_conversation[:200] + "...") # 只打印前200个字符

        print("开始分类分析...")
        classification_path = classify_conversation_hierarchical(
            cleaned_conversation,
            categories
        )
        print(f"分类完成，分类路径: {classification_path}")
        category_str = "-".join(classification_path)

        # 生成摘要
        print("开始生成对话摘要...")
        summary_prompt = create_summary_prompt(cleaned_conversation)
        summary = chat_with_model(summary_prompt)
        print("摘要生成完成")
        print(f"摘要内容：{summary[:100]}...")  # 只打印前100个字符

        return ConversationResponse(
            conversationId=request.conversationId,
            userNo=request.userNo,
            category=category_str,
            summary=summary,
            message="success"
        )
    except Exception as e:
        print(f"处理失败: {str(e)}")
        print(f"错误类型: {type(e)}")
        print(f"错误堆栈: ", e.__traceback__)
        return ConversationResponse(
            conversationId=request.conversationId,
            userNo=request.userNo,
            category="",
            summary="",
            message="fail"
        )


@app.get("/health")
async def health_check():
    return {
        "status": 200,
        "response": {
            "status": "healthy"
        },
        "message": "success"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)