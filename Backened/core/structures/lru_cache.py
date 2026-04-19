"""
[Data Structures] LRU 缓存
职责：提供 LRU (Least Recently Used) 缓存的实现，用于缓存频繁访问的数据。
"""
from typing import Dict, Any, Optional


class LRUCache:
    """
    LRU 缓存实现
    """
    def __init__(self, capacity: int):
        """
        初始化 LRU 缓存
        
        Args:
            capacity: 缓存容量
        """
        self.capacity = capacity
        self.cache: Dict[Any, Any] = {}
        self.order: list = []
    
    def get(self, key: Any) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在则返回 None
        """
        if key in self.cache:
            # 移动到最近使用
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: Any, value: Any):
        """
        放入缓存
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        if key in self.cache:
            # 更新值并移动到最近使用
            self.cache[key] = value
            self.order.remove(key)
            self.order.append(key)
        else:
            # 新键，检查容量
            if len(self.cache) >= self.capacity:
                # 删除最久未使用的
                oldest_key = self.order.pop(0)
                del self.cache[oldest_key]
            # 添加新键
            self.cache[key] = value
            self.order.append(key)
    
    def remove(self, key: Any):
        """
        移除缓存
        
        Args:
            key: 缓存键
        """
        if key in self.cache:
            del self.cache[key]
            self.order.remove(key)
    
    def clear(self):
        """
        清空缓存
        """
        self.cache.clear()
        self.order.clear()
