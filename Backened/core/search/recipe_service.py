"""
[Service] 菜谱服务类
职责：封装菜谱数据管理和搜索功能，提供高效的菜谱查询服务。
实施功能：
- 从 CSV 文件加载菜谱数据
- 构建前缀树、哈希索引等数据结构
- 提供按名称、食材、功效、适合体质搜索菜谱的功能
- 提供按多个食材搜索菜谱的功能
- 提供获取所有菜谱的功能
- 实现 LRU 缓存，提高查询性能
"""
from pathlib import Path
from typing import List, Optional, Union
from .recipe_loader import load_recipe_data
from models.recipe import Recipe
from core.structures.trie import Trie
from core.structures.hash_index import HashIndex
from core.structures.lru_cache import LRUCache


class RecipeService:
    """
    菜谱服务类
    封装菜谱数据管理和搜索功能
    """
    
    def __init__(self, file_path: Optional[Union[str, Path]] = None, cache_capacity: int = 128):
        """
        初始化菜谱服务
        
        Args:
            file_path: 数据文件路径
            cache_capacity: 缓存容量
        """
        self.file_path = file_path
        self.recipes = []
        self.recipe_by_id = {}
        self.name_trie = Trie()
        self.ingredient_index = HashIndex()
        self.effect_index = HashIndex()
        self.suitable_index = HashIndex()
        self.cache = LRUCache(cache_capacity)
        
        # 加载数据
        if file_path:
            self.load_data(file_path)

    def load_data(self, path: Optional[Union[str, Path]] = None) -> int:
        """
        从 CSV 文件加载菜谱数据
        返回加载条数
        
        Args:
            path: 数据文件路径
            
        Returns:
            加载的条数
        """
        p = path or self.file_path
        if not p:
            return 0
        
        # 加载数据
        self.recipes = load_recipe_data(p)
        
        # 构建索引
        self.recipe_by_id = {recipe.id: recipe for recipe in self.recipes}
        
        # 清空索引
        self.name_trie = Trie()
        self.ingredient_index = HashIndex()
        self.effect_index = HashIndex()
        self.suitable_index = HashIndex()
        
        # 构建索引
        for recipe in self.recipes:
            # 构建名称前缀树
            self.name_trie.insert(recipe.name)
            
            # 构建食材索引
            for ingredient in recipe.ingredients:
                self.ingredient_index.add(ingredient, recipe.id)
            
            # 构建功效索引
            for effect in recipe.effect:
                self.effect_index.add(effect, recipe.id)
            
            # 构建适合体质索引
            for suitable in recipe.suitable:
                self.suitable_index.add(suitable, recipe.id)
        
        return len(self.recipes)

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """
        根据 ID 获取菜谱
        
        Args:
            recipe_id: 菜谱 ID
            
        Returns:
            菜谱对象，如果不存在则返回 None
        """
        return self.recipe_by_id.get(recipe_id)

    def search_by_name(self, keyword: str) -> List[Recipe]:
        """
        按名称搜索菜谱
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的菜谱列表
        """
        # 生成缓存键
        cache_key = f"name:{keyword}"
        
        # 检查缓存
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # 搜索名称
        names = self.name_trie.search_prefix(keyword)
        result = [recipe for recipe in self.recipes if recipe.name in names]
        
        # 缓存结果
        self.cache.put(cache_key, result)
        
        return result

    def search_by_ingredient(self, ingredient: str) -> List[Recipe]:
        """
        按食材搜索菜谱
        
        Args:
            ingredient: 食材名称
            
        Returns:
            包含该食材的菜谱列表
        """
        # 生成缓存键
        cache_key = f"ingredient:{ingredient}"
        
        # 检查缓存
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # 搜索食材
        recipe_ids = self.ingredient_index.get(ingredient)
        result = [self.recipe_by_id[rid] for rid in recipe_ids if rid in self.recipe_by_id]
        
        # 缓存结果
        self.cache.put(cache_key, result)
        
        return result

    def search_by_effect(self, effect: str) -> List[Recipe]:
        """
        按功效搜索菜谱
        
        Args:
            effect: 功效
            
        Returns:
            具有该功效的菜谱列表
        """
        # 生成缓存键
        cache_key = f"effect:{effect}"
        
        # 检查缓存
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # 搜索功效
        recipe_ids = self.effect_index.get(effect)
        result = [self.recipe_by_id[rid] for rid in recipe_ids if rid in self.recipe_by_id]
        
        # 缓存结果
        self.cache.put(cache_key, result)
        
        return result

    def search_by_suitable(self, suitable: str) -> List[Recipe]:
        """
        按适合体质搜索菜谱
        
        Args:
            suitable: 体质类型
            
        Returns:
            适合该体质的菜谱列表
        """
        # 生成缓存键
        cache_key = f"suitable:{suitable}"
        
        # 检查缓存
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # 搜索适合体质
        recipe_ids = self.suitable_index.get(suitable)
        result = [self.recipe_by_id[rid] for rid in recipe_ids if rid in self.recipe_by_id]
        
        # 缓存结果
        self.cache.put(cache_key, result)
        
        return result

    def search_by_ingredients(self, ingredients: List[str]) -> List[Recipe]:
        """
        按多个食材搜索菜谱
        
        Args:
            ingredients: 食材列表
            
        Returns:
            包含所有指定食材的菜谱列表
        """
        # 生成缓存键
        cache_key = f"ingredients:{','.join(sorted(ingredients))}"
        
        # 检查缓存
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # 搜索多个食材
        if not ingredients:
            return []
        
        # 获取第一个食材的菜谱
        recipe_ids = set(self.ingredient_index.get(ingredients[0]))
        
        # 与其他食材的菜谱取交集
        for ingredient in ingredients[1:]:
            current_ids = set(self.ingredient_index.get(ingredient))
            recipe_ids.intersection_update(current_ids)
            if not recipe_ids:
                break
        
        result = [self.recipe_by_id[rid] for rid in recipe_ids if rid in self.recipe_by_id]
        
        # 缓存结果
        self.cache.put(cache_key, result)
        
        return result

    def get_all_recipes(self) -> List[Recipe]:
        """
        获取所有菜谱
        
        Returns:
            所有菜谱列表
        """
        return self.recipes
