"""
[Data Model] 食材数据模型
职责：定义食材相关的数据结构，包含食材的基本信息、标签、功效、适合体质、禁忌、食用方法、图片等字段。
实施功能：
- 定义 Ingredient 模型，包含 id、name、tag、effect、suitable、avoid、methods、images 等字段
- 支持分类、性味、描述、关联食疗方等可选字段的存储
- 为 FastAPI 提供数据验证和序列化支持
"""
from pydantic import BaseModel
from typing import List, Optional

class Ingredient(BaseModel):
    id: int
    name: str
    tag: str         # 标签/功效类别
    effect: str      # 具体功效
    suitable: str    # 适合体质
    avoid: str       # 禁忌
    methods: str     # 食用方法
    images: str      # 图片文件名
    category: Optional[str] = None  # 分类：五谷、蔬菜、肉禽等（可选）
    property: Optional[str] = None  # 性味：如“寒”、“温”（可选）
    description: Optional[str] = None  # 详细描述（可选）
    related_recipes: Optional[List[int]] = [] # 关联的食疗方 ID 集合
    ancient_quote: Optional[str] = ""  # 古籍考证/推荐理由