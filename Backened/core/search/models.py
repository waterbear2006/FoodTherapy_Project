"""
数据模型层 - Pydantic 校验
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
