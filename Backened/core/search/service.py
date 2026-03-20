"""
[Service] 食疗服务类
职责：封装食疗库核心索引操作，提供业务功能。
实施功能：
- 从 CSV 文件加载食疗数据
- 构建前缀树、哈希索引等数据结构
- 提供按名称、标签、体质搜索食疗的功能
- 提供全文检索功能
- 提供食材搭配和禁忌查询功能
- 提供食材组合推荐功能
- 实现 LRU 缓存，提高查询性能
"""
from pathlib import Path
from typing import List, Optional, Union
from .recipe_loader import load_recipe_data
from models.recipe import Recipe
from core.structures.trie import Trie
from core.structures.hash_index import HashIndex
from core.structures.lru_cache import LRUCache


class TherapyService:
    """
    食疗服务类
    封装核心索引操作，提供业务功能
    """
    
    def __init__(self, file_path: Optional[Union[str, Path]] = None, cache_capacity: int = 128):
        """
        初始化食疗服务
        
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
        从 CSV/Excel 加载并构建索引
        返回加载条数
        
        Args:
            path: 数据文件路径
            
        Returns:
            加载的条数
        """
        p = path or self.file_path
        if not p:
            return 0
        items = load_recipe_data(p)
        self.recipes = items
        self.recipe_by_id = {recipe.id: recipe for recipe in items}
        
        # 构建索引
        for recipe in items:
            self.name_trie.insert(recipe.name)
            for ingredient in recipe.ingredients:
                self.ingredient_index.add(ingredient, recipe.id)
            for effect in recipe.effect:
                self.effect_index.add(effect, recipe.id)
            for suitable in recipe.suitable:
                self.suitable_index.add(suitable, recipe.id)
        return len(items)

    def add_item(self, item: Recipe) -> None:
        """
        单条添加
        
        Args:
            item: 食疗详情
        """
        self.recipes.append(item)
        self.recipe_by_id[item.id] = item
        self.name_trie.insert(item.name)
        for ingredient in item.ingredients:
            self.ingredient_index.add(ingredient, item.id)
        for effect in item.effect:
            self.effect_index.add(effect, item.id)
        for suitable in item.suitable:
            self.suitable_index.add(suitable, item.id)

    def search_by_name(self, prefix: str) -> List[Recipe]:
        """
        按名称前缀搜索（Trie）
        
        Args:
            prefix: 名称前缀
            
        Returns:
            匹配的食疗详情列表
        """
        names = self.name_trie.search_prefix(prefix)
        return [recipe for recipe in self.recipes if recipe.name in names]

    def filter_by_tag(self, tag: str) -> List[Recipe]:
        """
        按功能标签筛选（Hash）
        
        Args:
            tag: 功能标签
            
        Returns:
            匹配的食疗详情列表
        """
        ids = self.effect_index.get(tag)
        return [self.recipe_by_id[i] for i in ids if i in self.recipe_by_id]

    def filter_by_constitution(self, constitution: str) -> List[Recipe]:
        """
        按体质筛选
        
        Args:
            constitution: 体质类型
            
        Returns:
            匹配的食疗详情列表
        """
        ids = self.suitable_index.get(constitution)
        return [self.recipe_by_id[i] for i in ids if i in self.recipe_by_id]

    def full_text_search(self, keyword: str) -> List[Recipe]:
        """
        全文检索
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的食疗详情列表
        """
        result = []
        for recipe in self.recipes:
            if keyword in recipe.name or \
               any(keyword in ingredient for ingredient in recipe.ingredients) or \
               any(keyword in effect for effect in recipe.effect) or \
               any(keyword in suitable for suitable in recipe.suitable) or \
               keyword in recipe.steps:
                result.append(recipe)
        return result

    def get_matches(self, ingredient: str) -> List[str]:
        """
        食材搭配
        
        Args:
            ingredient: 食材名称
            
        Returns:
            搭配的食材列表
        """
        # 简单实现：返回包含该食材的菜谱中的其他食材
        matches = set()
        recipe_ids = self.ingredient_index.get(ingredient)
        for recipe_id in recipe_ids:
            if recipe_id in self.recipe_by_id:
                recipe = self.recipe_by_id[recipe_id]
                for ing in recipe.ingredients:
                    if ing != ingredient:
                        matches.add(ing)
        return list(matches)

    def get_taboos(self, ingredient: str) -> List[str]:
        """
        食材禁忌
        
        Args:
            ingredient: 食材名称
            
        Returns:
            禁忌的食材列表
        """
        # 简单实现：返回空列表，实际应用中需要根据数据添加禁忌信息
        return []

    def find_compatible_combinations(
        self,
        start_ingredient: str,
        max_depth: int = 3,
    ) -> List[List[str]]:
        """
        DFS 组合寻优：搭配组合
        
        Args:
            start_ingredient: 起始食材
            max_depth: 最大深度
            
        Returns:
            兼容的食材组合列表
        """
        # 简单实现：返回包含起始食材的菜谱中的食材组合
        combinations = []
        recipe_ids = self.ingredient_index.get(start_ingredient)
        for recipe_id in recipe_ids:
            if recipe_id in self.recipe_by_id:
                recipe = self.recipe_by_id[recipe_id]
                if len(recipe.ingredients) >= 2:
                    combinations.append(recipe.ingredients)
        return combinations

    def query(
        self,
        keyword: str = "",
        tag: Optional[str] = None,
        constitution: Optional[str] = None,
        use_full_text: bool = False,
    ) -> List[Recipe]:
        """
        综合查询（带 LRU 缓存）
        
        Args:
            keyword: 搜索关键词
            tag: 功能标签
            constitution: 体质类型
            use_full_text: 是否使用全文检索
            
        Returns:
            匹配的食疗详情列表
        """
        # 生成缓存键
        cache_key = f"{keyword}|{tag}|{constitution}|{use_full_text}"
        
        # 检查缓存
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # 根据参数进行查询
        if use_full_text:
            result = self.full_text_search(keyword)
        elif tag:
            result = self.filter_by_tag(tag)
        elif constitution:
            result = self.filter_by_constitution(constitution)
        elif keyword:
            result = self.search_by_name(keyword)
        else:
            result = self.recipes
        
        # 缓存结果
        self.cache.put(cache_key, result)
        
        return result
