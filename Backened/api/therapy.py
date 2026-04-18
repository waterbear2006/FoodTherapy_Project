"""
[API Router] 食疗库接口
职责：提供食疗相关的 API 接口，包括搜索、筛选、食材搭配等功能。
实施功能：
- 搜索食疗，支持关键词、标签、体质筛选
- 获取食材搭配
- 获取食材禁忌
- 获取食材组合
- 获取所有功能标签
- 获取所有体质类型
- 从 caipu.csv 文件加载食疗数据
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from models.recipe import Recipe
from core.search.service import TherapyService
from pathlib import Path

router = APIRouter(tags=["食疗库"])

# 初始化食疗服务
therapy_service = TherapyService()

# 加载食疗数据（菜谱库/食疗库使用 caipu.csv）
data_path = Path(__file__).resolve().parent.parent / "data" / "caipu.csv"
if data_path.exists():
    loaded_count = therapy_service.load_data(data_path)
    print(f"[Therapy] 成功加载 {loaded_count} 条食疗数据")
else:
    print(f"[Therapy] 警告：未找到数据文件 {data_path}")


@router.get("/search", response_model=List[Recipe])
async def search_therapy(
    keyword: str = Query("", description="搜索关键词"),
    tag: Optional[str] = Query(None, description="功能标签"),
    constitution: Optional[str] = Query(None, description="体质类型"),
    suitable: Optional[str] = Query(None, description="体质类型（与constitution相同，兼容前端参数）"),
    use_full_text: bool = Query(False, description="是否使用全文检索")
):
    """
    搜索食疗
    支持按关键词、功能标签、体质类型进行搜索
    """
    # 兼容前端使用的 suitable 参数名
    constitution_value = constitution or suitable
    result = therapy_service.query(
        keyword=keyword,
        tag=tag,
        constitution=constitution_value,
        use_full_text=use_full_text
    )
    return result


@router.get("/ingredient/matches/{ingredient}", response_model=List[str])
async def get_ingredient_matches(ingredient: str):
    """
    获取食材搭配
    """
    matches = therapy_service.get_matches(ingredient)
    return matches


@router.get("/ingredient/taboos/{ingredient}", response_model=List[str])
async def get_ingredient_taboos(ingredient: str):
    """
    获取食材禁忌
    """
    taboos = therapy_service.get_taboos(ingredient)
    return taboos


@router.get("/combinations/{ingredient}", response_model=List[List[str]])
async def get_ingredient_combinations(
    ingredient: str,
    max_depth: int = Query(3, description="最大深度")
):
    """
    获取食材组合
    使用 DFS 算法寻找兼容的食材组合
    """
    combinations = therapy_service.find_compatible_combinations(
        start_ingredient=ingredient,
        max_depth=max_depth
    )
    return combinations


@router.get("/tags", response_model=List[str])
async def get_all_tags():
    """
    获取所有功能标签
    """
    # 从已加载的数据中提取所有功能标签（来自 Recipe.effect）
    all_items = therapy_service.query()
    tags = set()
    for item in all_items:
        # item.effect 是 List[str]
        tags.update(item.effect or [])
    return sorted(tags)


@router.get("/constitutions", response_model=List[str])
async def get_all_constitutions():
    """
    获取所有体质类型
    """
    # 从已加载的数据中提取所有体质类型（来自 Recipe.suitable）
    all_items = therapy_service.query()
    constitutions = set()
    for item in all_items:
        constitutions.update(item.suitable or [])
    return sorted(constitutions)
