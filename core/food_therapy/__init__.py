"""
食疗库核心模块
90%+ 代码为数据结构与算法实现

此文件仅做整洁导出，便于上层直接使用:

    from core.food_therapy import TherapyService, TherapyDetail
"""
from .models import TherapyDetail, IngredientInfo, ConstitutionType
from .therapy_core import FoodTherapyIndex
from .service import TherapyService

__all__ = [
    "TherapyDetail",
    "IngredientInfo",
    "ConstitutionType",
    "FoodTherapyIndex",
    "TherapyService",
]
