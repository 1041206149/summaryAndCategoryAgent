"""
分类提示词模板
将硬编码的提示词抽离为独立模块
"""
from typing import List, Optional, Dict
from models.schemas import CategoryData


class ClassificationPrompts:
    """分类提示词管理"""

    @classmethod
    def create_prompt(
        cls,
        conversation: str,
        available_categories: List[str],
        current_path: List[str] = None,
        level: int = 1,
        categories: Optional[CategoryData] = None,
        include_conversation: bool = True
    ) -> str:
        """
        创建分类提示词

        Args:
            conversation: 对话内容
            available_categories: 可选分类列表
            current_path: 当前分类路径
            level: 分类级别
            categories: 分类数据对象（包含描述和示例）
            include_conversation: 是否包含对话内容（首轮True，后续False）

        Returns:
            格式化的提示词
        """
        current_path = current_path or []
        level_names = {1: "一级", 2: "二级", 3: "三级"}

        if level == 1:
            # 一级分类提示词（首轮必须包含对话内容）
            categories_str = cls._build_level1_categories_str(available_categories, categories)

            prompt = f"""作为专业的对话分类分析师，请对以下对话进行一级分类。请注意，一级分类是最重要的，它决定了后续的分类方向。

当前分类层级: 一级分类

当前对话内容:
{conversation}

可选的一级分类及其含义:
{categories_str}

分类规则：
1. 仔细阅读对话内容，准确判断主要诉求
2. 根据主要诉求选择最匹配的一级分类
3. **只输出【】中的分类名称，不要输出"说明"或"示例"的内容**
4. 必须从上述【】选项中选择，不能创建新的分类
5. 如果对话内容涉及多个分类，选择最主要的诉求对应的分类
6. 如果实在无法确定具体类别，再选择"其他"类

请直接输出一个分类名称（只输出【】里的内容）。"""
        else:
            # 二级/三级分类提示词（多轮对话模式，不重复对话内容）
            categories_str = cls._build_other_level_categories_str(
                available_categories, level, current_path, categories
            )
            current_path_str = " > ".join(current_path)

            prompt = f"""现在进行{level_names[level]}分类。

【之前的分类决策】
你已经将上述对话归类为：{current_path_str}

【当前任务】
请在此基础上，继续细化分类，选择最合适的{level_names[level]}分类。

【可选的{level_names[level]}分类】
{categories_str}

【分类规则】
1. 只能从上述【】分类选项中选择一个
2. **只输出【】中的分类名称，不要输出"说明"或"示例"的内容**
3. 确保输出的分类名称与【】内的选项完全一致
4. 结合之前的分类决策，选择最符合对话内容的细分类别

【特别提示】
- 如果二级分类为"飞享会员"，重点区分：
  * 【取消扣款】：用户要求退款、退费、取消扣费
  * 【取消续费】：用户要求停止自动续费、关闭续费功能
  * 若未明确提到"续费"字眼，通常选择【取消扣款】

请直接输出一个分类名称（只输出【】里的内容）。"""

        return prompt

    @classmethod
    def _build_level1_categories_str(
        cls,
        available_categories: List[str],
        categories: Optional[CategoryData]
    ) -> str:
        """构建一级分类字符串（带描述和示例）"""
        if not categories:
            # 如果没有提供categories对象，返回简单格式
            return "\n".join([f"【{cat}】" for cat in available_categories])

        result = []
        for cat_name in available_categories:
            # 从categories.level1中查找对应的分类信息
            cat_info = None
            for cat_id, info in categories.level1.items():
                if info['name'] == cat_name:
                    cat_info = info
                    break

            if cat_info:
                desc = cat_info.get('description', '')
                example = cat_info.get('example', '')

                # 分类名称用【】包裹，更清晰
                line = f"【{cat_name}】"

                # 描述和示例单独一行，使用缩进和说明文字
                extra_info = []
                if desc:
                    extra_info.append(f"  说明：{desc}")
                if example and str(example).strip() and str(example) != 'nan':
                    extra_info.append(f"  示例：{example}")

                if extra_info:
                    line += "\n" + "\n".join(extra_info)

                result.append(line)
            else:
                result.append(f"【{cat_name}】")

        return "\n".join(result)

    @classmethod
    def _build_other_level_categories_str(
        cls,
        available_categories: List[str],
        level: int,
        current_path: List[str],
        categories: Optional[CategoryData]
    ) -> str:
        """构建二级/三级分类字符串（带描述和示例）"""
        if not categories:
            # 如果没有提供categories对象，返回简单格式
            return "\n".join([f"【{cat}】" for cat in available_categories])

        result = []
        for cat_name in available_categories:
            cat_info = None

            if level == 2:
                # 从level2中查找
                cat_info = categories.level2.get(cat_name)
            elif level == 3:
                # 从level3中查找
                cat_info = categories.level3.get(cat_name)

            if cat_info:
                desc = cat_info.get('description', '')
                example = cat_info.get('example', '')

                # 分类名称用【】包裹，更清晰
                line = f"【{cat_name}】"

                # 描述和示例单独一行，使用缩进和说明文字
                extra_info = []
                if desc:
                    extra_info.append(f"  说明：{desc}")
                if example and str(example).strip() and str(example) != 'nan':
                    extra_info.append(f"  示例：{example}")

                if extra_info:
                    line += "\n" + "\n".join(extra_info)

                result.append(line)
            else:
                result.append(f"【{cat_name}】")

        return "\n".join(result)
