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
