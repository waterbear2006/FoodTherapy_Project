"""
食疗库核心索引
整合：Trie + Hash 索引 + LRU + 图 + KMP + DFS
"""
from typing import List, Optional, Set, Dict, Any

from core.foodtherapy.models import TherapyDetail
from core.structures import Trie, HashIndex, LRUCache, AdjacencyGraph
from core.algorithms import KMPMatcher, dfs_visit, dfs_paths


class FoodTherapyIndex:
    """
    手搓数据结构中心
    90% 算法逻辑在此
    """

    def __init__(self, cache_capacity: int = 128):
        self._storage: Dict[int, TherapyDetail] = {}
        self._tag_index = HashIndex()
        self._constitution_index = HashIndex()
        self._name_trie = Trie()
        self._cache = LRUCache[str, List[TherapyDetail]](cache_capacity)
        self._ingredient_graph = AdjacencyGraph()

    def add_item(self, item: TherapyDetail) -> None:
        """插入并构建多维度索引"""
        self._storage[item.id] = item
        for tag in item.tags:
            self._tag_index.add(tag, item.id)
        for con in item.constitution:
            self._constitution_index.add(con, item.id)
        self._name_trie.insert(item.name, item.id)
        for m in item.matches:
            self._ingredient_graph.add_edge(item.name, m, "match")
        for t in item.taboos:
            self._ingredient_graph.add_edge(item.name, t, "taboo")

    def search_by_name(self, prefix: str) -> List[TherapyDetail]:
        """Trie 前缀搜索 + DFS 收集"""
        ids = self._name_trie.search_prefix(prefix)
        return [self._storage[i] for i in ids]

    def filter_by_tag(self, tag: str) -> List[TherapyDetail]:
        """Hash 索引 O(1) 分类"""
        ids = self._tag_index.get(tag)
        return [self._storage[i] for i in ids]

    def filter_by_constitution(self, constitution: str) -> List[TherapyDetail]:
        """体质匹配"""
        ids = self._constitution_index.get(constitution)
        return [self._storage[i] for i in ids]

    def full_text_search(self, keyword: str, fields: Optional[List[str]] = None) -> List[TherapyDetail]:
        """
        KMP 全文检索
        在 methods, matches, taboos 等字段中搜索 keyword
        """
        if not keyword.strip():
            return []
        kmp = KMPMatcher(keyword)
        default_fields = ["methods", "matches", "taboos", "tags"]
        fields = fields or default_fields
        result_ids: Set[int] = set()
        for item in self._storage.values():
            for f in fields:
                val = getattr(item, f, None)
                if val is None:
                    continue
                text = val if isinstance(val, str) else ",".join(val) if isinstance(val, list) else str(val)
                if kmp.contains(text):
                    result_ids.add(item.id)
                    break
        return [self._storage[i] for i in result_ids]

    def get_matches(self, ingredient: str) -> List[str]:
        """获取食材搭配"""
        return self._ingredient_graph.get_matches(ingredient)

    def get_taboos(self, ingredient: str) -> List[str]:
        """获取食材禁忌"""
        return self._ingredient_graph.get_taboos(ingredient)

    def find_compatible_combinations(
        self,
        start: str,
        max_depth: int = 3,
        exclude_taboos: bool = True,
    ) -> List[List[str]]:
        """
        DFS 组合寻优：从 start 出发，找所有搭配路径
        排除禁忌组合
        """
        match_graph = self._ingredient_graph.to_match_graph()
        taboo_set = self._ingredient_graph.to_taboo_set() if exclude_taboos else set()
        paths: List[List[str]] = []

        def _has_taboo_with_path(node: str, path: List[str]) -> bool:
            if not exclude_taboos:
                return False
            return any((x, node) in taboo_set or (node, x) in taboo_set for x in path)

        def _dfs(path: List[str], u: str, depth: int) -> None:
            if depth > max_depth:
                return
            path.append(u)
            if len(path) >= 2:
                paths.append(path[:])
            for v in match_graph.get(u, []):
                if v not in path and not _has_taboo_with_path(v, path):
                    _dfs(path, v, depth + 1)
            path.pop()

        _dfs([], start, 0)
        return paths

    def query_with_cache(
        self,
        keyword: str,
        tag: Optional[str] = None,
        constitution: Optional[str] = None,
        use_full_text: bool = False,
    ) -> List[TherapyDetail]:
        """
        综合查询，带 LRU 缓存
        """
        cache_key = f"{keyword}|{tag}|{constitution}|{use_full_text}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        if use_full_text:
            result = self.full_text_search(keyword)
        elif tag:
            result = self.filter_by_tag(tag)
        elif constitution:
            result = self.filter_by_constitution(constitution)
        elif keyword:
            result = self.search_by_name(keyword)
        else:
            result = list(self._storage.values())
        self._cache.put(cache_key, result)
        return result
