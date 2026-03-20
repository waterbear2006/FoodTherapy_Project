"""
[API Router] 菜谱接口
职责：提供菜谱相关的 API 接口，包括获取菜谱列表、获取菜谱详情、搜索菜谱等功能。
实施功能：
- 获取所有菜谱列表
- 获取菜谱详情
- 按名称搜索菜谱
- 按食材搜索菜谱
- 按功效搜索菜谱
- 按适合体质搜索菜谱
- 按多个食材搜索菜谱
- 从 caipu.csv 文件加载菜谱数据
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from models.recipe import Recipe
from core.search.recipe_service import RecipeService
from pathlib import Path

router = APIRouter(prefix="/api/recipes", tags=["菜谱模块"])

# 初始化菜谱服务
recipe_service = RecipeService()

# 加载菜谱数据
data_path = Path(__file__).resolve().parent.parent / "data" / "caipu.csv"
if data_path.exists():
    loaded_count = recipe_service.load_data(data_path)
    print(f"🚀 [Recipes] 成功加载 {loaded_count} 条菜谱数据")
else:
    print(f"⚠️ [Recipes] 警告：未找到数据文件 {data_path}")


@router.get("/", response_model=List[Recipe])
async def list_recipes():
    """
    获取所有菜谱
    """
    recipes = recipe_service.get_all_recipes()
    return recipes


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    """
    获取菜谱详情
    """
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    return recipe


@router.get("/search/name", response_model=List[Recipe])
async def search_recipes_by_name(
    keyword: str = Query(..., description="搜索关键词")
):
    """
    按名称搜索菜谱
    """
    recipes = recipe_service.search_by_name(keyword)
    return recipes


@router.get("/search/ingredient", response_model=List[Recipe])
async def search_recipes_by_ingredient(
    ingredient: str = Query(..., description="食材名称")
):
    """
    按食材搜索菜谱
    """
    recipes = recipe_service.search_by_ingredient(ingredient)
    return recipes


@router.get("/search/effect", response_model=List[Recipe])
async def search_recipes_by_effect(
    effect: str = Query(..., description="功效")
):
    """
    按功效搜索菜谱
    """
    recipes = recipe_service.search_by_effect(effect)
    return recipes


@router.get("/search/suitable", response_model=List[Recipe])
async def search_recipes_by_suitable(
    suitable: str = Query(..., description="适合体质")
):
    """
    按适合体质搜索菜谱
    """
    recipes = recipe_service.search_by_suitable(suitable)
    return recipes


@router.post("/search/ingredients", response_model=List[Recipe])
async def search_recipes_by_ingredients(
    ingredients: List[str]
):
    """
    按多个食材搜索菜谱
    """
    recipes = recipe_service.search_by_ingredients(ingredients)
    return recipes
