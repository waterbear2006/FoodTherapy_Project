"""
图结构：邻接表实现
用于食材搭配（正向边）、禁忌（负向/禁止边）
结合 DFS 做组合寻优
"""
from typing import List, Dict, Set, Tuple, Any, Optional
from collections import defaultdict


class AdjacencyGraph:
    """
    手写邻接表图
    - 支持有向/无向
    - 支持多关系：搭配(正向)、禁忌(负向)
    """

    def __init__(self):
        # 邻接表：node -> [(neighbor, edge_type)]
        # edge_type: "match" 搭配, "taboo" 禁忌
        self._adj: Dict[Any, List[Tuple[Any, str]]] = defaultdict(list)
        self._nodes: Set[Any] = set()

    def add_node(self, node: Any) -> None:
        self._nodes.add(node)

    def add_edge(self, u: Any, v: Any, edge_type: str = "match") -> None:
        """添加边"""
        self._nodes.add(u)
        self._nodes.add(v)
        self._adj[u].append((v, edge_type))

    def get_matches(self, node: Any) -> List[Any]:
        """获取搭配的邻居"""
        return [v for v, t in self._adj.get(node, []) if t == "match"]

    def get_taboos(self, node: Any) -> List[Any]:
        """获取禁忌的邻居"""
        return [v for v, t in self._adj.get(node, []) if t == "taboo"]

    def get_neighbors(self, node: Any, edge_type: Optional[str] = None) -> List[Any]:
        """获取邻居，可选过滤边类型"""
        if edge_type is None:
            return [v for v, _ in self._adj.get(node, [])]
        return [v for v, t in self._adj.get(node, []) if t == edge_type]

    def to_match_graph(self) -> Dict[Any, List[Any]]:
        """转为仅搭配的邻接表，供 DFS 使用"""
        return {n: self.get_matches(n) for n in self._nodes}

    def to_taboo_set(self) -> Set[Tuple[Any, Any]]:
        """禁忌对集合"""
        out: Set[Tuple[Any, Any]] = set()
        for u, edges in self._adj.items():
            for v, t in edges:
                if t == "taboo":
                    out.add((u, v))
                    out.add((v, u))
        return out

    def has_taboo(self, a: Any, b: Any) -> bool:
        """是否禁忌"""
        taboos = self.to_taboo_set()
        return (a, b) in taboos or (b, a) in taboos
