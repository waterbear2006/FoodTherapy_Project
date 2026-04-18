"""
[API Router] 搜索接口
职责：提供搜索相关的 API 接口，包含食材搜索、分类和菜谱推荐功能。
实施功能：
- 搜索食材，支持关键词搜索和多条件筛选
- 获取所有食材的功效标签
- 获取所有食材的适合体质
- 获取所有食材的分类
- 根据用户现有食材推荐菜谱
- 获取所有菜谱
- 支持食材名称的模糊搜索
- 支持按标签、体质、分类筛选食材
"""
# search.py - 定义搜索相关的 API 路由，包含食材搜索和根据现有食材推荐菜谱的功能。

"""
搜索模块 API 接口说明

该模块包含以下功能：

1. 食材搜索功能：
   - GET /api/search/ingredients - 搜索食材，支持关键词搜索和多条件筛选
   - GET /api/search/tags - 获取所有食材的功效标签
   - GET /api/search/constitutions - 获取所有食材的适合体质
   - GET /api/search/categories - 获取所有食材的分类

2. 菜谱推荐功能：
   - POST /api/search/recipes - 根据用户现有食材推荐菜谱
   - GET /api/search/recipes/all - 获取所有菜谱

使用说明：

1. 食材搜索：
   - 关键词搜索：通过 keyword 参数搜索食材名称
   - 标签筛选：通过 tag 参数按功效标签筛选
   - 体质筛选：通过 suitable 参数按适合体质筛选
   - 分类筛选：通过 category 参数按分类筛选

2. 菜谱推荐：
   - 通过 ingredients 参数传入用户现有的食材列表
   - 系统会根据食材匹配度推荐菜谱
   - 返回结果按匹配度排序
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from pathlib import Path
import re
from pydantic import BaseModel
import anyio

from models.ingredient import Ingredient
from core.preloader import ingredient_db, ingredient_trie
from core.search.recipe_service import RecipeService
import time

router = APIRouter(tags=["搜索模块"])

# 缓存菜谱搜索结果
recipe_cache = {}

# 初始化菜谱服务（真实读取 caipu.csv）
recipe_service = RecipeService()
_caipu_path = Path(__file__).resolve().parent.parent / "data" / "caipu.csv"
if _caipu_path.exists():
    recipe_service.load_data(_caipu_path)
else:
    print(f"[Search] 未找到数据文件: {_caipu_path}")


def split_multi(value: Optional[str]) -> List[str]:
    """把 CSV 的"多值字段"拆成数组（兼容 、/，/空格 等分隔符）。"""
    if not value:
        return []
    return [p.strip() for p in re.split(r"[、，,/;\s]+", value) if p.strip()]

@router.get("/ingredients", response_model=List[Ingredient])
async def search_ingredients(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    tag: Optional[str] = Query(None, description="按功效标签筛选"),
    suitable: Optional[str] = Query(None, description="按适合体质筛选"),
    category: Optional[str] = Query(None, description="按分类筛选")
):
    """
    搜索食材，支持关键词搜索和多条件筛选
    
    - **keyword**: 搜索关键词，支持模糊匹配食材名称
    - **tag**: 功效标签，如"补气"、"滋阴"等
    - **suitable**: 适合体质，如"气虚质"、"阳虚质"等
    - **category**: 分类，如"五谷"、"蔬菜"等
    """
    # 初始化为所有食材
    results = list(ingredient_db.values())
    
    # 关键词搜索：支持食材名/功效/适合体质/禁忌/方法 的包含匹配
    if keyword:
        kw = keyword.strip()
        matched_names = ingredient_trie.search_prefix(kw)

        def _contains(item: dict, field: str) -> bool:
            val = item.get(field)
            if not val:
                return False
            return kw in str(val)

        results = [
            item for item in results
            if item.get("name") in matched_names
            or kw in str(item.get("name", ""))
            or _contains(item, "tag")
            or _contains(item, "effect")
            or _contains(item, "suitable")
            or _contains(item, "avoid")
            or _contains(item, "methods")
            or _contains(item, "ancient_books")
        ]
    
    # 按功效标签筛选
    if tag:
        results = [item for item in results if tag in split_multi(item.get("tag"))]
    
    # 按适合体质筛选
    if suitable:
        results = [item for item in results if suitable in split_multi(item.get("suitable"))]
    
    # 按分类筛选
    if category:
        results = [item for item in results if item["category"] == category]
    
    return results

@router.get("/tags")
async def get_all_tags():
    """
    获取所有食材的功效标签
    """
    tags = set()
    for ingredient in ingredient_db.values():
        tags.update(split_multi(ingredient.get("tag")))

    return {"tags": sorted(tags)}

@router.get("/constitutions")
async def get_all_constitutions():
    """
    获取所有食材的适合体质
    """
    constitutions = set()
    for ingredient in ingredient_db.values():
        constitutions.update(split_multi(ingredient.get("suitable")))

    return {"constitutions": sorted(constitutions)}

@router.get("/categories")
async def get_all_categories():
    """
    获取所有食材的分类（从 tag 字段提取）
    """
    categories = set()
    for ingredient in ingredient_db.values():
        # 从 tag 字段提取分类，支持多个标签（如"补气、滋阴"）
        tag_str = ingredient.get("tag", "")
        if tag_str:
            # 处理多种分隔符：、，,/
            import re
            tags = re.split(r'[、，,\/\s]+', tag_str)
            for tag in tags:
                tag = tag.strip()
                if tag:
                    categories.add(tag)
    
    # 添加"全部"选项并排序
    sorted_categories = sorted(categories)
    return {"categories": ["全部"] + sorted_categories}

@router.post("/recipes")
async def search_recipes_by_ingredients(
    ingredients: List[str] = Body(..., description="用户现有的食材列表")
):
    """
    根据用户输入的现有食材，推荐可能的菜谱

    - **ingredients**: 用户现有的食材列表，如 ["黄芪", "鸡肉", "大枣"]
    """
    try:
        # 使用缓存键（将食材列表转为元组以作为字典键）
        cache_key = tuple(sorted(ingredients))
        current_time = time.time()

        # 检查缓存是否存在且未过期（5分钟有效期）
        if cache_key in recipe_cache:
            cached_result, cached_time = recipe_cache[cache_key]
            if current_time - cached_time < 300:
                return cached_result

        # 菜谱推荐算法：
        # 1) 遍历真实菜谱库（caipu.csv）
        # 2) 计算匹配食材集合交集大小
        # 3) match_score = 交集数量 / 菜谱所需食材数量
        matched_recipes = []
        for recipe in recipe_service.get_all_recipes():
            matched_ingredients = set(ingredients) & set(recipe.ingredients)
            match_count = len(matched_ingredients)

            if recipe.ingredients:
                match_score = match_count / len(recipe.ingredients)
            else:
                match_score = 0

            if match_score > 0:
                matched_recipes.append({
                    "id": recipe.id,
                    "name": recipe.name,
                    "ingredients": recipe.ingredients,
                    "effect": recipe.effect,
                    "suitable": recipe.suitable,
                    "description": "、".join(recipe.effect) if recipe.effect else "",
                    "steps": recipe.steps,
                    "images": recipe.images,
                    "taboo": getattr(recipe, 'taboo', ''),
                    "match_score": match_score,
                    "matched_ingredients": list(matched_ingredients)
                })

        matched_recipes.sort(key=lambda x: x["match_score"], reverse=True)

        result = {
            "status": "success",
            "data": matched_recipes,
            "message": f"找到 {len(matched_recipes)} 个匹配的菜谱"
        }

        # 缓存结果
        recipe_cache[cache_key] = (result, current_time)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索菜谱时发生错误: {str(e)}")


class RecipeGenerateRequest(BaseModel):
    ingredients: List[str]
    constitution: Optional[str] = None


@router.post("/recipes/generate", summary="根据食材+体质生成匹配菜谱")
async def generate_recipes(req: RecipeGenerateRequest):
    """
    与 /api/search/recipes 类似，但允许传入用户体质以增强推荐相关性。
    """
    try:
        if not req.ingredients:
            return {"status": "success", "data": [], "message": "未传入食材"}

        matched_recipes = []
        for recipe in recipe_service.get_all_recipes():
            matched_ingredients = set(req.ingredients) & set(recipe.ingredients)
            match_count = len(matched_ingredients)
            if not recipe.ingredients:
                continue

            match_score = match_count / len(recipe.ingredients)

            # 体质加权：命中体质适合条件则加分
            if req.constitution and req.constitution in (recipe.suitable or []):
                match_score *= 1.2

            if match_score > 0:
                matched_recipes.append({
                    "id": recipe.id,
                    "name": recipe.name,
                    "ingredients": recipe.ingredients,
                    "effect": recipe.effect,
                    "suitable": recipe.suitable,
                    "description": "、".join(recipe.effect) if recipe.effect else "",
                    "steps": recipe.steps,
                    "images": recipe.images,
                    "taboo": getattr(recipe, 'taboo', ''),
                    "match_score": match_score,
                    "matched_ingredients": list(matched_ingredients),
                })

        matched_recipes.sort(key=lambda x: x["match_score"], reverse=True)
        result = {
            "status": "success",
            "data": matched_recipes,
            "message": f"找到 {len(matched_recipes)} 个匹配的菜谱",
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成菜谱时发生错误: {str(e)}")

@router.get("/recipes/all")
async def get_all_recipes():
    """
    获取所有菜谱
    """
    return {
        "status": "success",
        "data": recipe_service.get_all_recipes()
    }

@router.get("/recipes/popular")
async def get_popular_recipes(limit: int = Query(5, description="返回数量")):
    """
    获取热门菜谱（按匹配度排序）
    """
    try:
        all_recipes = recipe_service.get_all_recipes()
        # 返回前 limit 个菜谱作为热门推荐
        popular = all_recipes[:limit] if len(all_recipes) > limit else all_recipes
        
        return {
            "status": "success",
            "items": popular,
            "message": f"返回 {len(popular)} 个热门菜谱"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门菜谱失败：{str(e)}")


# ========== 健康养生新闻接口 ==========

# 导入新闻服务
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from service.news import get_food_news

@router.get("/news")
async def get_health_news():
    """
    获取健康养生新闻列表
    
    从 RSS 源获取与健康、养生、食疗相关的新闻资讯
    """
    try:
        # 使用 anyio.to_thread.run_sync 将同步阻塞函数移入线程池，防止阻塞事件循环
        news_data = await anyio.to_thread.run_sync(get_food_news)
        
        # 如果 RSS 获取失败或为空，返回兜底数据
        if not news_data:
            news_data = [
                {
                    "title": "春季养生：养肝护脾的黄金时节",
                    "summary": "春季是万物复苏的季节，也是养肝护脾的关键时期。中医认为，春气通肝，肝气旺盛，此时应注意调养肝脏，同时兼顾脾胃健康。",
                    "source": "中医养生堂",
                    "image": "",
                    "link": "#"
                },
                {
                    "title": "山药的药用价值与食疗功效",
                    "summary": "山药既是食材也是药材，具有健脾益胃、补肾益精的功效，适合多种体质人群食用。",
                    "source": "药膳食疗",
                    "image": "",
                    "link": "#"
                },
                {
                    "title": "九种体质的辨识与调理方法",
                    "summary": "了解自身体质类型，才能做到精准养生。中医将人体体质分为九种类型，每种体质有不同的特点和调理方案。",
                    "source": "国医在线",
                    "image": "",
                    "link": "#"
                }
            ]
        
        return {
            "status": "success",
            "data": news_data,
            "total": len(news_data)
        }
    except Exception as e:
        print(f"[News API] 获取新闻失败: {e}")
        # 返回兜底数据
        return {
            "status": "success",
            "data": [
                {
                    "title": "春季养生：养肝护脾的黄金时节",
                    "summary": "春季是万物复苏的季节，也是养肝护脾的关键时期。",
                    "source": "中医养生堂",
                    "image": "",
                    "link": "#"
                }
            ],
            "total": 1
        }
