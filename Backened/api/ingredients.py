<<<<<<< HEAD
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
=======
from pathlib import Path
from typing import List
>>>>>>> 5509c1398c0685e011f840fcbbe6dd0969d7e3cb

from fastapi import APIRouter, HTTPException, Query

<<<<<<< HEAD
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
=======
from core.food_therapy.models import IngredientInfo, TherapyDetail
from core.food_therapy.service import TherapyService


router = APIRouter()


def _create_service() -> TherapyService:
    """
    为 API 层创建共享的业务服务实例并加载数据.
    默认从项目根目录下的 therapy_data.csv 加载.
    """
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "therapy_data.csv"
    service = TherapyService(file_path=data_path)
    # 懒加载：文件不存在时不报错，只是返回 0
    service.load_data()
    return service


_service: TherapyService = _create_service()


@router.get(
    "/",
    response_model=List[IngredientInfo],
    summary="食材基础信息列表",
)
def list_ingredients(keyword: str = Query("", description="按名称前缀过滤（使用 Trie）")):
    """
    调用 core.structures 中的 Trie 实现前缀搜索, 返回基础食材信息视图.
    """
    items: List[TherapyDetail] = (
        _service.search_by_name(keyword) if keyword else _service.query(keyword="")
    )
    ingredients: List[IngredientInfo] = [
        IngredientInfo(id=i.id, name=i.name, tags=i.tags, constitution=i.constitution)
        for i in items
    ]
    return ingredients


@router.get(
    "/{ingredient_name}/matches",
    response_model=List[str],
    summary="查询某食材的搭配建议",
)
def get_ingredient_matches(ingredient_name: str):
    """
    基于核心图结构查询「宜配」食材.
    """
    matches = _service.get_matches(ingredient_name)
    if not matches:
        raise HTTPException(status_code=404, detail="未找到搭配信息")
    return matches


@router.get(
    "/{ingredient_name}/taboos",
    response_model=List[str],
    summary="查询某食材的禁忌搭配",
)
def get_ingredient_taboos(ingredient_name: str):
    """
    基于核心图结构查询「相克 / 禁忌」食材.
    """
    taboos = _service.get_taboos(ingredient_name)
    if not taboos:
        raise HTTPException(status_code=404, detail="未找到禁忌信息")
    return taboos

>>>>>>> 5509c1398c0685e011f840fcbbe6dd0969d7e3cb
