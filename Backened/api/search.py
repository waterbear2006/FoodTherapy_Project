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

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.ingredient import Ingredient
from core.preloader import recipe_hash_index, ingredient_db, ingredient_trie

router = APIRouter(prefix="/api/search", tags=["搜索模块"])

# 模拟菜谱数据
recipes_data = [
    {
        "id": 1,
        "name": "黄芪鸡汤",
        "ingredients": ["黄芪", "鸡肉", "大枣"],
        "description": "补气养血，适合气虚质、阳虚质",
        "steps": ["将黄芪、鸡肉、大枣洗净", "放入锅中，加水炖煮", "大火烧开后转小火煮1小时", "加盐调味即可"]
    },
    {
        "id": 2,
        "name": "山药粥",
        "ingredients": ["山药", "大米"],
        "description": "健脾养胃，适合脾虚质、气虚质",
        "steps": ["将山药去皮切块", "大米洗净", "放入锅中，加水煮粥", "煮至大米熟烂即可"]
    },
    {
        "id": 3,
        "name": "银耳百合汤",
        "ingredients": ["银耳", "百合", "枸杞"],
        "description": "滋阴润肺，适合阴虚质",
        "steps": ["将银耳泡发", "百合、枸杞洗净", "放入锅中，加水炖煮", "煮至银耳软烂，加冰糖调味"]
    },
    {
        "id": 4,
        "name": "生姜羊肉汤",
        "ingredients": ["生姜", "羊肉", "当归"],
        "description": "温阳散寒，适合阳虚质",
        "steps": ["将羊肉切块焯水", "生姜切片", "当归洗净", "放入锅中，加水炖煮", "大火烧开后转小火煮2小时", "加盐调味即可"]
    },
    {
        "id": 5,
        "name": "绿豆汤",
        "ingredients": ["绿豆", "百合"],
        "description": "清热解毒，适合湿热质",
        "steps": ["将绿豆、百合洗净", "放入锅中，加水煮至绿豆开花", "加冰糖调味即可"]
    }
]

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
    
    # 关键词搜索
    if keyword:
        # 使用前缀树进行关键词匹配
        matched_names = ingredient_trie.search_prefix(keyword)
        results = [item for item in results if item["name"] in matched_names]
    
    # 按功效标签筛选
    if tag:
        results = [item for item in results if tag in item["tag"]]
    
    # 按适合体质筛选
    if suitable:
        results = [item for item in results if suitable in item["suitable"]]
    
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
        if ingredient.get("tag"):
            # 处理多个标签的情况，如"补气/滋阴"
            tag_list = ingredient["tag"].split("/")
            for tag in tag_list:
                tags.add(tag.strip())
    
    return {"tags": list(tags)}

@router.get("/constitutions")
async def get_all_constitutions():
    """
    获取所有食材的适合体质
    """
    constitutions = set()
    for ingredient in ingredient_db.values():
        if ingredient.get("suitable"):
            # 处理多个体质的情况，如"气虚质/阳虚质"
            constitution_list = ingredient["suitable"].split("/")
            for constitution in constitution_list:
                constitutions.add(constitution.strip())
    
    return {"constitutions": list(constitutions)}

@router.get("/categories")
async def get_all_categories():
    """
    获取所有食材的分类
    """
    categories = set()
    for ingredient in ingredient_db.values():
        if ingredient.get("category"):
            categories.add(ingredient["category"])
    
    return {"categories": list(categories)}

@router.post("/recipes")
async def search_recipes_by_ingredients(
    ingredients: List[str] = Query(..., description="用户现有的食材列表")
):
    """
    根据用户输入的现有食材，推荐可能的菜谱
    
    - **ingredients**: 用户现有的食材列表，如 ["黄芪", "鸡肉", "大枣"]
    """
    try:
        # 简单的菜谱推荐算法
        # 1. 遍历所有菜谱
        # 2. 计算每个菜谱与用户现有食材的匹配度
        # 3. 按匹配度排序，返回匹配度高的菜谱
        
        matched_recipes = []
        
        for recipe in recipes_data:
            # 计算匹配的食材数量
            matched_ingredients = set(ingredients) & set(recipe["ingredients"])
            match_count = len(matched_ingredients)
            
            # 计算匹配度（匹配的食材数量 / 菜谱所需食材数量）
            if recipe["ingredients"]:
                match_score = match_count / len(recipe["ingredients"])
            else:
                match_score = 0
            
            # 只添加匹配度大于0的菜谱
            if match_score > 0:
                matched_recipes.append({
                    "id": recipe["id"],
                    "name": recipe["name"],
                    "ingredients": recipe["ingredients"],
                    "description": recipe["description"],
                    "steps": recipe["steps"],
                    "match_score": match_score,
                    "matched_ingredients": list(matched_ingredients)
                })
        
        # 按匹配度排序
        matched_recipes.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "status": "success",
            "data": matched_recipes,
            "message": f"找到 {len(matched_recipes)} 个匹配的菜谱"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索菜谱时发生错误: {str(e)}")

@router.get("/recipes/all")
async def get_all_recipes():
    """
    获取所有菜谱
    """
    return {
        "status": "success",
        "data": recipes_data
    }
