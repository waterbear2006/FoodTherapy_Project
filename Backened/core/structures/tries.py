"""
[Data Structures] 前缀树 (Trie)
职责：高效存储所有食材/症状关键词，支持前缀搜索。
"""
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search_prefix(self, prefix: str):
        """返回所有以该前缀开头的词"""
        node = self.root
        for char in prefix:
            if char not in node.children: return []
            node = node.children[char]
        
        results = []
        self._dfs_collect(node, prefix, results)
        return results

    def _dfs_collect(self, node, path, results):
        if node.is_end: results.append(path)
        for char, next_node in node.children.items():
            self._dfs_collect(next_node, path + char, results)