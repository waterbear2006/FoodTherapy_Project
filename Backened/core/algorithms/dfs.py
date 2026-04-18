"""
[Core Algorithms] 深度优先搜索 (带体质剪枝)
职责：在图谱中根据已有食材寻找食谱，并跳过包含禁忌食材的路径。
"""
def reverse_search_recipes(graph, available_ingredients, taboo_ingredients):
    """
    available_ingredients: 用户手头的食材 [山药, 排骨]
    taboo_ingredients: 用户不能吃的食材 [西瓜, 苦瓜] (基于体质判定)
    """
    recommended_recipes = []
    
    # 1. 从用户提供的每一个食材出发进行搜索
    for ing in available_ingredients:
        candidates = graph.get_neighbors(ing)
        
        for recipe in candidates:
            # 2. 剪枝逻辑：检查该食谱的所有成分
            recipe_contents = graph.get_neighbors(recipe)
            
            # 如果食谱中包含任何“禁忌食材”，直接丢弃该分支 (Pruning)
            is_taboo = any(item in taboo_ingredients for item in recipe_contents)
            if is_taboo:
                continue 
            
            # 3. 计算匹配度：你手头的食材占这道菜所需食材的比例
            match_count = sum(1 for item in recipe_contents if item in available_ingredients)
            match_rate = match_count / len(recipe_contents)
            
            recommended_recipes.append({
                "recipe": recipe,
                "match_rate": round(match_rate, 2),
                "contents": recipe_contents
            })
            
    # 按匹配度从高到低排序
    return sorted(recommended_recipes, key=lambda x: x['match_rate'], reverse=True)