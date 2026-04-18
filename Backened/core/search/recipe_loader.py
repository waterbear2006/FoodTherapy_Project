"""
[Data Loader] 菜谱数据加载器
职责：从 CSV 文件加载菜谱数据，解析数据并创建 Recipe 对象。
实施功能：
- 从 CSV 文件读取菜谱数据
- 解析食材、功效、适合体质等列表数据
- 创建并返回 Recipe 对象列表
- 处理数据加载过程中的异常
"""
import csv
from typing import List, Optional, Union
from pathlib import Path
from models.recipe import Recipe


def load_recipe_data(file_path: Union[str, Path]) -> List[Recipe]:
    """
    从 CSV 文件加载菜谱数据
    
    Args:
        file_path: CSV 文件路径
        
    Returns:
        菜谱列表
    """
    recipe_items = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 解析数据
                id = int(row.get('id', 0))
                name = row.get('name', '')
                
                # 解析食材，处理多个食材的情况
                ingredients_str = row.get('ingredients', '')
                ingredients = [ingredient.strip() for ingredient in ingredients_str.split('、') if ingredient.strip()]
                
                # 解析功效
                effect_str = row.get('effect', '')
                effect = [eff.strip() for eff in effect_str.split('、') if eff.strip()]
                
                # 解析适合体质
                suitable_str = row.get('suitable', '')
                suitable = [suit.strip() for suit in suitable_str.split('、') if suit.strip()]
                
                # 解析制作步骤
                steps = row.get('steps', '')
                
                # 解析图片文件名
                images = row.get('images', '')
                
                # 解析忌口
                taboo = row.get('taboo', '')
                
                # 创建 Recipe 对象
                recipe_item = Recipe(
                    id=id,
                    name=name,
                    ingredients=ingredients,
                    effect=effect,
                    suitable=suitable,
                    steps=steps,
                    images=images,
                    taboo=taboo,
                    ancient_books=row.get('AncientBooks', '') or row.get('ancient_books', '')
                )
                
                recipe_items.append(recipe_item)
    except Exception as e:
        print(f"加载菜谱数据失败: {e}")
    
    return recipe_items
