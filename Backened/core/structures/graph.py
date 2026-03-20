"""
[Data Structures] 邻接图
职责：提供图结构的实现，用于食材搭配和禁忌关系的存储。
"""
from typing import Dict, List, Set, Tuple


class AdjacencyGraph:
    """
    邻接图实现
    """
    def __init__(self):
        self._graph = {}
    
    def add_edge(self, u: str, v: str, relation: str):
        """
        添加边，记录关系类型
        """
        if u not in self._graph:
            self._graph[u] = {}
        if relation not in self._graph[u]:
            self._graph[u][relation] = []
        if v not in self._graph[u][relation]:
            self._graph[u][relation].append(v)
    
    def get_edges(self, u: str, relation: str = None) -> List[str]:
        """
        获取节点 u 的边
        """
        if u not in self._graph:
            return []
        if relation:
            return self._graph[u].get(relation, [])
        else:
            result = []
            for rel_edges in self._graph[u].values():
                result.extend(rel_edges)
            return result
    
    def get_matches(self, ingredient: str) -> List[str]:
        """
        获取食材的搭配
        """
        return self.get_edges(ingredient, "match")
    
    def get_taboos(self, ingredient: str) -> List[str]:
        """
        获取食材的禁忌
        """
        return self.get_edges(ingredient, "taboo")
    
    def to_match_graph(self) -> Dict[str, List[str]]:
        """
        转换为只包含搭配关系的图
        """
        match_graph = {}
        for u, relations in self._graph.items():
            if "match" in relations:
                match_graph[u] = relations["match"]
        return match_graph
    
    def to_taboo_set(self) -> Set[Tuple[str, str]]:
        """
        转换为禁忌关系集合
        """
        taboo_set = set()
        for u, relations in self._graph.items():
            if "taboo" in relations:
                for v in relations["taboo"]:
                    taboo_set.add((u, v))
                    taboo_set.add((v, u))
        return taboo_set
    
    def clear(self):
        """
        清空图
        """
        self._graph.clear()
