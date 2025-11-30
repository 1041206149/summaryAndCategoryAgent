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
        categories: Optional[CategoryData] = None
    ) -> str:
        """
        创建分类提示词

        Args:
            conversation: 对话内容
            available_categories: 可选分类列表
            current_path: 当前分类路径
            level: 分类级别
            categories: 分类数据对象（包含描述和示例）

        Returns:
            格式化的提示词
        """
        current_path = current_path or []
        level_names = {1: "一级", 2: "二级", 3: "三级"}

        if level == 1:
            # 一级分类提示词
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
3. 只输出分类名称，不要输出任何解释
4. 必须从上述选项中选择，不能创建新的分类
5. 如果对话内容涉及多个分类，选择最主要的诉求对应的分类
6. 如果实在无法确定具体类别，再选择"其他"类

请直接输出一个分类名称。"""
        else:
            # 二级/三级分类提示词
            categories_str = cls._build_other_level_categories_str(
                available_categories, level, current_path, categories
            )
            current_path_str = " > ".join(current_path)

            prompt = f"""作为专业的对话分类分析师,请对以下对话进行{level_names[level]}分类。

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

    @classmethod
    def _build_level1_categories_str(
        cls,
        available_categories: List[str],
        categories: Optional[CategoryData]
    ) -> str:
        """构建一级分类字符串（带描述和示例）"""
        if not categories:
            # 如果没有提供categories对象，返回简单格式
            return "\n".join([f"● {cat}" for cat in available_categories])

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

                if desc:
                    line = f"● {cat_name}\n  └─ {desc}"
                    # 只有当example不为空且不是NaN时才添加
                    if example and str(example).strip() and str(example) != 'nan':
                        line += f"\n  └─ 示例: {example}"
                    result.append(line)
                else:
                    result.append(f"● {cat_name}")
            else:
                result.append(f"● {cat_name}")

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
            return "\n".join([f"● {cat}" for cat in available_categories])

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

                if desc:
                    line = f"● {cat_name}\n  └─ {desc}"
                    # 只有当example不为空且不是NaN时才添加
                    if example and str(example).strip() and str(example) != 'nan':
                        line += f"\n  └─ 示例: {example}"
                    result.append(line)
                else:
                    result.append(f"● {cat_name}")
            else:
                result.append(f"● {cat_name}")

        return "\n".join(result)
