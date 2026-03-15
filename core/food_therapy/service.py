"""
业务服务层
"""
from pathlib import Path
from typing import List, Optional, Union

from .models import TherapyDetail
from .therapy_core import FoodTherapyIndex
from .data_loader import load_therapy_data


class TherapyService:
    def __init__(self, file_path: Optional[Union[str, Path]] = None, cache_capacity: int = 128):
        self.index = FoodTherapyIndex(cache_capacity=cache_capacity)
        self.file_path = file_path

    def load_data(self, path: Optional[Union[str, Path]] = None) -> int:
        """
        从 CSV/Excel 加载并构建索引
        返回加载条数
        """
        p = path or self.file_path
        if not p:
            return 0
        items = load_therapy_data(p)
        for item in items:
            self.index.add_item(item)
        return len(items)

    def add_item(self, item: TherapyDetail) -> None:
        """单条添加"""
        self.index.add_item(item)

    def search_by_name(self, prefix: str) -> List[TherapyDetail]:
        """按名称前缀搜索（Trie）"""
        return self.index.search_by_name(prefix)

    def filter_by_tag(self, tag: str) -> List[TherapyDetail]:
        """按功能标签筛选（Hash）"""
        return self.index.filter_by_tag(tag)

    def filter_by_constitution(self, constitution: str) -> List[TherapyDetail]:
        """按体质筛选"""
        return self.index.filter_by_constitution(constitution)

    def full_text_search(self, keyword: str) -> List[TherapyDetail]:
        """KMP 全文检索"""
        return self.index.full_text_search(keyword)

    def get_matches(self, ingredient: str) -> List[str]:
        """食材搭配"""
        return self.index.get_matches(ingredient)

    def get_taboos(self, ingredient: str) -> List[str]:
        """食材禁忌"""
        return self.index.get_taboos(ingredient)

    def find_compatible_combinations(
        self,
        start_ingredient: str,
        max_depth: int = 3,
    ) -> List[List[str]]:
        """DFS 组合寻优：搭配组合"""
        return self.index.find_compatible_combinations(
            start_ingredient, max_depth=max_depth, exclude_taboos=True
        )

    def query(
        self,
        keyword: str = "",
        tag: Optional[str] = None,
        constitution: Optional[str] = None,
        use_full_text: bool = False,
    ) -> List[TherapyDetail]:
        """综合查询（带 LRU 缓存）"""
        return self.index.query_with_cache(
            keyword, tag=tag, constitution=constitution, use_full_text=use_full_text
        )
