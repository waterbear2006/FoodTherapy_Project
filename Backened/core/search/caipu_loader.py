"""
食谱数据加载器
从 caipu.csv 文件加载食谱数据
"""
import csv
from typing import List, Optional, Union
from pathlib import Path


class Recipe:
    """食谱类"""
    def __init__(self, id: int, name: str, ingredients: str, effect: str, 
                 suitable: str, steps: str, taboo: str, images: str):
        self.id = id
        self.name = name
        self.ingredients = ingredients
        self.effect = effect
        self.suitable = suitable
        self.steps = steps
        self.taboo = taboo
        self.images = images


def load_caipu_data(file_path: Union[str, Path]) -> List[Recipe]:
    """
    从 CSV 文件加载食谱数据
    
    Args:
        file_path: CSV 文件路径
        
    Returns:
        食谱列表
    """
    recipes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 解析数据
                id = int(row.get('id', 0))
                name = row.get('name', '')
                ingredients = row.get('ingredients', '')
                effect = row.get('effect', '')
                suitable = row.get('suitable', '')
                steps = row.get('steps', '')
                taboo = row.get('taboo', '')
                images = row.get('images', '')
                
                # 创建 Recipe 对象
                recipe = Recipe(
                    id=id,
                    name=name,
                    ingredients=ingredients,
                    effect=effect,
                    suitable=suitable,
                    steps=steps,
                    taboo=taboo,
                    images=images
                )
                
                recipes.append(recipe)
    except Exception as e:
        print(f"加载食谱数据失败: {e}")
    
    return recipes


def search_recipes_by_keyword(recipes: List[Recipe], keyword: str) -> List[Recipe]:
    """
    根据关键词搜索食谱
    
    Args:
        recipes: 食谱列表
        keyword: 搜索关键词
        
    Returns:
        匹配的食谱列表
    """
    keyword = keyword.lower()
    matched_recipes = []
    
    for recipe in recipes:
        # 在名称、食材、功效、适用体质中搜索
        if (keyword in recipe.name.lower() or 
            keyword in recipe.ingredients.lower() or 
            keyword in recipe.effect.lower() or 
            keyword in recipe.suitable.lower()):
            matched_recipes.append(recipe)
    
    return matched_recipes


def search_recipes_by_constitution(recipes: List[Recipe], constitution: str) -> List[Recipe]:
    """
    根据体质搜索食谱
    
    Args:
        recipes: 食谱列表
        constitution: 体质类型
        
    Returns:
        匹配的食谱列表
    """
    constitution = constitution.lower()
    matched_recipes = []
    
    for recipe in recipes:
        if constitution in recipe.suitable.lower():
            matched_recipes.append(recipe)
    
    return matched_recipes
