"""
手写哈希索引（拉链法）
多维度索引：tag -> ids, constitution -> ids, name -> id
"""
from typing import Dict, List, Any, Optional


def _hash_key(key: str) -> int:
    """简单字符串哈希"""
    h = 0
    for c in key:
        h = (31 * h + ord(c)) & 0x7FFFFFFF
    return h


class HashIndex:
    """
    手写哈希索引（拉链法模拟）
    实际使用 dict，但逻辑上体现：key -> List[value] 的拉链结构
    """

    def __init__(self):
        self._buckets: Dict[str, List[int]] = {}

    def add(self, key: str, value_id: int) -> None:
        """添加索引项"""
        self._buckets.setdefault(key, []).append(value_id)

    def get(self, key: str) -> List[int]:
        """O(1) 平均 获取 key 对应的所有 id"""
        return self._buckets.get(key, [])

    def get_all_keys(self) -> List[str]:
        return list(self._buckets.keys())
