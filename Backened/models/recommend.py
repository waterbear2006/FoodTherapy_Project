"""
[Data Models] 智能推荐传输模型
职责：定义包含疗法、食疗、食材的多维度推荐协议。
"""
from pydantic import BaseModel
from typing import List, Optional

class RecommendItem(BaseModel):
    title: str
    reason: str  # 推荐理由，这里将由 AI 生成
    image_url: Optional[str] = None

class RecommendationResponse(BaseModel):
    constitution: str
    summary: str  # 健康档案摘要
    therapies: List[RecommendItem]   # 推荐疗法
    recipes: List[RecommendItem]     # 推荐食疗
    ingredients: List[RecommendItem] # 推荐食材