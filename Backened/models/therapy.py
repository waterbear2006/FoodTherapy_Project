"""
[Data Model] 食疗数据模型
职责：定义食疗相关的数据结构，包含食疗的基本信息、标签、制作方法、搭配食材、禁忌、适用体质等字段。
实施功能：
- 定义 TherapyDetail 模型，包含 id、name、tags、methods、matches、taboos、constitution 等字段
- 支持标签列表、搭配食材列表、禁忌列表、适用体质列表的存储
- 为 FastAPI 提供数据验证和序列化支持
"""
from typing import List
from pydantic import BaseModel, Field


class TherapyDetail(BaseModel):
    """食疗详情"""
    id: int
    name: str
    tags: List[str] = Field(default_factory=list)      # 如：["补气", "去湿"]
    methods: str = ""                                  # 制作方法
    matches: List[str] = Field(default_factory=list)   # 食材搭配
    taboos: List[str] = Field(default_factory=list)    # 禁忌
    constitution: List[str] = Field(default_factory=list)  # 适用体质


class IngredientInfo(BaseModel):
    """食材信息（用于搭配/禁忌图）"""
    id: int
    name: str
    tags: List[str] = Field(default_factory=list)
    constitution: List[str] = Field(default_factory=list)


class ConstitutionType(BaseModel):
    """体质类型"""
    name: str
    compatible_tags: List[str] = Field(default_factory=list)
    incompatible_tags: List[str] = Field(default_factory=list)
