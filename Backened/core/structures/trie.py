"""
[Data Structures] 前缀树 (Trie)
职责：实现高效的字符串前缀匹配，用于食材名称的快速搜索。
"""


class TrieNode:
    """
    前缀树节点
    """
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    """
    前缀树实现
    """
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        """
        插入单词到前缀树
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
    
    def search(self, word):
        """
        搜索单词是否存在于前缀树中
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word
    
    def starts_with(self, prefix):
        """
        检查是否有以 prefix 为前缀的单词
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
    
    def search_prefix(self, prefix):
        """
        搜索所有以 prefix 为前缀的单词
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        result = []
        self._collect_words(node, prefix, result)
        return result
    
    def _collect_words(self, node, current_word, result):
        """
        递归收集所有单词
        """
        if node.is_end_of_word:
            result.append(current_word)
        for char, child_node in node.children.items():
            self._collect_words(child_node, current_word + char, result)
