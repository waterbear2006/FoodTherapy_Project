from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Query

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

