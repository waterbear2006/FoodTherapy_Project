# 追加内容到 search.py
therapy_endpoints = """


# ========== 食疗方相关接口 ==========

@router.get("/therapy/search")
async def search_therapy(
    suitable: Optional[str] = Query(None, description="按适合体质筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词")
):
    try:
        all_recipes = recipe_service.get_all_recipes()
        results = all_recipes
        
        if suitable:
            results = [r for r in results if suitable in (r.suitable or [])]
        
        if keyword:
            kw = keyword.strip()
            results = [r for r in results if kw in r.name or any(kw in e for e in (r.effect or []))]
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索食疗方失败：{str(e)}")


@router.get("/therapy/constitutions")
async def get_therapy_constitutions():
    try:
        constitutions = set()
        all_recipes = recipe_service.get_all_recipes()
        
        for recipe in all_recipes:
            if recipe.suitable:
                constitutions.update(recipe.suitable)
        
        return sorted(list(constitutions))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取体质列表失败：{str(e)}")
"""

with open('search.py', 'a', encoding='utf-8') as f:
    f.write(therapy_endpoints)

print("Successfully appended therapy endpoints to search.py!")
