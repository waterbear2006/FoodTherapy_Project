"""
[Data Structures] 哈希索引
职责：提供哈希索引的实现。
"""


class HashIndex:
    """
    哈希索引实现
    """
    def __init__(self):
        self._index = {}
    
    def add(self, key, value):
        """
        添加键值对
        """
        if key not in self._index:
            self._index[key] = []
        self._index[key].append(value)
    
    def get(self, key):
        """
        获取键对应的值列表
        """
        return self._index.get(key, [])
    
    def remove(self, key, value):
        """
        移除键对应的值
        """
        if key in self._index:
            if value in self._index[key]:
                self._index[key].remove(value)
                if not self._index[key]:
                    del self._index[key]
    
    def clear(self):
        """
        清空索引
        """
        self._index.clear()
