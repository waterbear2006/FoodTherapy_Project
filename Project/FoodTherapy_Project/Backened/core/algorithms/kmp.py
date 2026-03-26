"""
KMP 字符串匹配算法
用于全文检索：在制作方法、搭配、禁忌等长文本中搜索关键词
"""
from typing import List, Iterator


class KMPMatcher:
    """
    KMP (Knuth-Morris-Pratt) 字符串匹配
    - 预处理 O(m)，匹配 O(n)，m=模式长，n=文本长
    - 相比暴力 O(n*m) 更高效
    """

    def __init__(self, pattern: str):
        self.pattern = pattern
        self._next = self._build_next(pattern)

    @staticmethod
    def _build_next(p: str) -> List[int]:
        """构建 next 数组（失败函数）"""
        m = len(p)
        next_arr = [0] * (m + 1)
        i, j = 0, -1
        next_arr[0] = -1
        while i < m:
            if j == -1 or p[i] == p[j]:
                i += 1
                j += 1
                next_arr[i] = j
            else:
                j = next_arr[j]
        return next_arr

    def search(self, text: str) -> List[int]:
        """返回 text 中所有匹配的起始下标"""
        n, m = len(text), len(self.pattern)
        if m == 0:
            return list(range(n + 1))
        res: List[int] = []
        i = j = 0
        while i < n:
            if j == -1 or text[i] == self.pattern[j]:
                i += 1
                j += 1
                if j == m:
                    res.append(i - m)
                    j = self._next[j]
            else:
                j = self._next[j]
        return res

    def find_all(self, text: str) -> Iterator[int]:
        """迭代器形式"""
        for pos in self.search(text):
            yield pos

    def contains(self, text: str) -> bool:
        """是否存在匹配"""
        return len(self.search(text)) > 0
