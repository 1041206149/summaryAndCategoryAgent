"""
分类数据加载工具
"""
import pandas as pd
from pathlib import Path
from langchain.tools import BaseTool
from pydantic import BaseModel
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
