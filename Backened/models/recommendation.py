"""
[Data Model] 推荐数据模型
职责：定义推荐相关的数据结构，包含推荐项目、推荐理由、推荐结果等字段。
实施功能：
- 定义 RecommendationItem 模型，包含 title 和 reason 字段
- 定义 RecommendationResponse 模型，包含体质、节气、季节、年龄、性别、推荐总结、推荐疗法、推荐食谱、推荐食材等字段
- 为 FastAPI 提供数据验证和序列化支持
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class RecommendationItem(BaseModel):
    """
    推荐项目模型
    """
    id: Optional[int] = Field(None, description="项目真实ID")
    title: str = Field(..., description="推荐项目标题")
    reason: str = Field(..., description="推荐理由")
    image: Optional[str] = Field(None, description="真实图片名称")
    ancient_quote: Optional[str] = Field(None, description="医典原文/RAG证据")

class RecommendationResponse(BaseModel):
    """
    推荐响应模型
    """
    constitution: str = Field(..., description="用户体质")
    solar_term: str = Field(..., description="当前节气")
    season: str = Field(..., description="当前季节")
    age: Optional[int] = Field(None, description="用户年龄")
    gender: Optional[str] = Field(None, description="用户性别")
    summary: str = Field(..., description="推荐总结")
    therapies: List[RecommendationItem] = Field(..., description="推荐疗法")
    recipes: List[RecommendationItem] = Field(..., description="推荐食谱")
    ingredients: List[RecommendationItem] = Field(..., description="推荐食材")
