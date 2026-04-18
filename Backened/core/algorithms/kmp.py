"""
[Core Algorithms] KMP 字符串匹配
职责：在长文本中高效定位特定食材，时间复杂度 $O(M + N)$。
"""

class KMPMatcher:
    def _get_next(self, pattern: str):
        next_arr = [0] * len(pattern)
        j = 0
        for i in range(1, len(pattern)):
            while j > 0 and pattern[i] != pattern[j]:
                j = next_arr[j-1]
            if pattern[i] == pattern[pattern[j]]:
                j += 1
            next_arr[i] = j
        return next_arr

    def search(self, text: str, pattern: str) -> bool:
        if not pattern: return True
        next_arr = self._get_next(pattern)
        j = 0
        for i in range(len(text)):
            while j > 0 and text[i] != pattern[j]:
                j = next_arr[j-1]
            if text[i] == pattern[j]:
                j += 1
            if j == len(pattern):
                return True
        return False