from fastapi import APIRouter, HTTPException
from typing import List
from models.ingredient import Ingredient
from core.preloader import ingredient_db

router = APIRouter(prefix="/api/ingredients", tags=["食材库模块"])

@router.get("/", response_model=List[Ingredient])
async def list_ingredients(category: Optional[str] = None):
    """获取所有食材，支持按分类筛选 [cite: 7]"""
    all_items = list(ingredient_db.values())
    if category:
        return [item for item in all_items if item["category"] == category]
    return all_items

@router.get("/{item_id}", response_model=Ingredient)
async def get_ingredient(item_id: int):
    """获取特定食材详情（性味归经、功效等） [cite: 4, 7]"""
    if item_id not in ingredient_db:
        raise HTTPException(status_code=404, detail="该食材不存在于智库中")
    return ingredient_db[item_id]