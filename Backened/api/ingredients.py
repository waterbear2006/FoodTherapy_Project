"""

[API Router] 食材库接口
职责：定义食材库相关的 API 路由，包含获取食材列表和获取特定食材详情两大功能。
实施功能：
- 获取所有食材列表，支持按分类筛选
- 获取特定食材的详细信息，包括标签、功效、适合体质、禁忌、食用方法、图片等
- 从 shicai.csv 文件加载食材数据
"""
# ingredients.py - 定义食材库相关的 API 路由，包含获取食材列表和获取特定食材详情两大功能。

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.ingredient import Ingredient
from core.preloader import ingredient_db

router = APIRouter(prefix="/api/ingredients", tags=["食材库模块"])

@router.get("/", response_model=List[Ingredient])
async def list_ingredients(category: Optional[str] = None, tag: Optional[str] = None, suitable: Optional[str] = None):
    """获取所有食材，支持按分类、标签和适合体质筛选"""
    all_items = list(ingredient_db.values())
    
    # 按分类筛选
    if category:
        all_items = [item for item in all_items if item["category"] == category]
    
    # 按标签筛选
    if tag:
        all_items = [item for item in all_items if tag in item["tag"]]
    
    # 按适合体质筛选
    if suitable:
        all_items = [item for item in all_items if suitable in item["suitable"]]
    
    return all_items

@router.get("/{item_id}", response_model=Ingredient)
async def get_ingredient(item_id: int):
    """获取特定食材详情（功效、适合体质、禁忌等）"""
    if item_id not in ingredient_db:
        raise HTTPException(status_code=404, detail="该食材不存在于智库中")
    return ingredient_db[item_id]