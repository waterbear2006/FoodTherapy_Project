from pydantic import BaseModel
from typing import List, Optional

class Ingredient(BaseModel):
    id: int
    name: str
    category: str         # 分类：五谷、蔬菜、肉禽等
    property: str         # 性味：如“寒”、“温”
    flavor: str           # 归经/功效
    description: str      # 详细描述
    related_recipes: Optional[List[int]] = [] # 关联的食疗方 ID 集合