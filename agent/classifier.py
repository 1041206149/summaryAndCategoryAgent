"""
分类Agent
负责执行三级分类逻辑（支持多轮对话记忆）
"""
from typing import List, Dict
from loguru import logger
from tools.classify_level import ClassifyLevelTool
from models.schemas import CategoryData, ClassificationResult


class ClassificationAgent:
    """分类Agent（带对话历史记忆）"""

    def __init__(self, categories: CategoryData):
        """
        初始化分类Agent

        Args:
            categories: 分类数据
        """
        self.categories = categories
        self.classify_tool = ClassifyLevelTool(categories=categories)
        logger.debug("分类Agent初始化完成")

    def classify(self, cleaned_conversation: str) -> ClassificationResult:
        """
        执行三级分类（多轮对话模式）

        Args:
            cleaned_conversation: 清洗后的对话

        Returns:
            分类结果
        """
        logger.info("开始分层分类（多轮对话模式）...")
        classification_path = []
        chat_history = []  # 初始化对话历史

        # 一级分类
        level1_categories = self._get_level1_categories()
        logger.debug(f"一级分类选项: {level1_categories}")
        level1, chat_history = self.classify_tool._run(
            conversation=cleaned_conversation,
            available_categories=level1_categories,
            current_path=[],
            level=1,
            chat_history=chat_history
        )
        classification_path.append(level1)
        logger.info(f"一级分类: {level1}")
        logger.debug(f"对话历史长度: {len(chat_history)}")

        # 二级分类（携带一级分类的历史）
        level2_categories = self._get_level2_categories(level1)
        logger.debug(f"二级分类选项: {level2_categories}")
        level2, chat_history = self.classify_tool._run(
            conversation=cleaned_conversation,
            available_categories=level2_categories,
            current_path=classification_path,
            level=2,
            chat_history=chat_history  # 传入历史
        )
        classification_path.append(level2)
        logger.info(f"二级分类: {level2}")
        logger.debug(f"对话历史长度: {len(chat_history)}")

        # 三级分类 (如果需要，携带一二级分类的历史)
        level3 = None
        if level2 in self.categories.level3_parents:
            level3_categories = self._get_level3_categories(level2)
            logger.debug(f"三级分类选项: {level3_categories}")
            level3, chat_history = self.classify_tool._run(
                conversation=cleaned_conversation,
                available_categories=level3_categories,
                current_path=classification_path,
                level=3,
                chat_history=chat_history  # 传入历史
            )
            classification_path.append(level3)
            logger.info(f"三级分类: {level3}")
            logger.debug(f"对话历史长度: {len(chat_history)}")

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
