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

    class Config:
        arbitrary_types_allowed = True


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
