"""
深度优先搜索 (DFS)
用于：图遍历、路径查找、组合寻优
"""
from typing import List, Set, Dict, Callable, Any, Optional


def dfs_visit(
    graph: Dict[Any, List[Any]],
    start: Any,
    visited: Optional[Set[Any]] = None,
    on_visit: Optional[Callable[[Any], None]] = None,
) -> Set[Any]:
    """
    从 start 出发 DFS 遍历图
    graph: 邻接表 {node -> [neighbors]}
    返回访问过的节点集合
    """
    if visited is None:
        visited = set()
    stack = [start]
    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        if on_visit:
            on_visit(u)
        for v in graph.get(u, []):
            if v not in visited:
                stack.append(v)
    return visited


def dfs_paths(
    graph: Dict[Any, List[Any]],
    start: Any,
    end: Any,
    max_depth: int = 10,
) -> List[List[Any]]:
    """
    DFS 查找 start -> end 的所有简单路径
    用于食材搭配组合寻优
    """
    if start == end:
        return [[start]]
    paths: List[List[Any]] = []
    path: List[Any] = []
    visited: Set[Any] = set()

    def _dfs(u: Any, depth: int) -> None:
        if depth > max_depth:
            return
        path.append(u)
        visited.add(u)
        if u == end:
            paths.append(path[:])
        else:
            for v in graph.get(u, []):
                if v not in visited:
                    _dfs(v, depth + 1)
        path.pop()
        visited.discard(u)

    _dfs(start, 0)
    return paths
