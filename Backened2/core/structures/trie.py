"""
手写前缀树 (Trie / 字典树)
用于食材名、标签的前缀搜索
"""
from typing import List, Dict, Optional, Set, Any

T = type(None)  # 占位，实际存任意类型


class TrieNode:
    """前缀树节点"""
    __slots__ = ("children", "is_end", "data_ids")

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end = False
        self.data_ids: Set[int] = set()  # 支持多 ID 共享同一路径


class Trie:
    """
    手写前缀树
    - 插入 O(m)，m 为键长
    - 前缀搜索 O(m + k)，k 为匹配数量
    """

    def __init__(self):
        self._root = TrieNode()

    def insert(self, key: str, data_id: int) -> None:
        """插入键与关联 ID"""
        node = self._root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.data_ids.add(data_id)

    def search_prefix(self, prefix: str) -> Set[int]:
        """前缀匹配，返回所有 data_id 集合"""
        node = self._root
        for char in prefix:
            if char not in node.children:
                return set()
            node = node.children[char]
        ids: Set[int] = set()
        self._dfs_collect_ids(node, ids)
        return ids

    def _dfs_collect_ids(self, node: TrieNode, out: Set[int]) -> None:
        """DFS 收集该子树下所有 data_id"""
        if node.is_end:
            out.update(node.data_ids)
        for child in node.children.values():
            self._dfs_collect_ids(child, out)

    def search_exact(self, key: str) -> Set[int]:
        """精确匹配"""
        node = self._root
        for char in key:
            if char not in node.children:
                return set()
            node = node.children[char]
        return node.data_ids if node.is_end else set()
