"""
[Data Model] 菜谱数据模型
职责：定义菜谱相关的数据结构，包含菜谱的基本信息、食材、功效、适合体质等字段。
实施功能：
- 定义 Recipe 模型，包含 id、name、ingredients、effect、suitable、steps、images 等字段
- 支持食材列表、功效列表、适合体质列表的存储
- 为 FastAPI 提供数据验证和序列化支持
"""
from typing import List
from pydantic import BaseModel, Field


class Recipe(BaseModel):
    """菜谱模型"""
    id: int
    name: str
    ingredients: List[str] = Field(default_factory=list)  # 食材列表
    effect: List[str] = Field(default_factory=list)        # 功效列表
    suitable: List[str] = Field(default_factory=list)      # 适合体质列表
    steps: str = ""                                      # 制作步骤
    images: str = ""                                     # 图片文件名
    taboo: str = ""                                      # 忌口
    ancient_quote: str = ""                              # 古籍考证/推荐理由
