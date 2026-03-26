"""
<<<<<<< HEAD
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
=======
LRU Cache：哈希表 (Hash Map) + 双向链表 (Doubly Linked List)
- Hash Map: key -> (value, DListNode) 实现 O(1) 查找
- 双向链表: 头=最近使用，尾=最久未使用，O(1) 头插、O(1) 尾删
"""
from typing import Generic, TypeVar, Optional, Dict

from .linked_list import DListNode

K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    """
    手写 LRU 缓存
    组合：Hash Map + 双向链表
    - get/put 均 O(1)
    - 超出容量时淘汰最久未使用（尾删 O(1)）
    """

    def __init__(self, capacity: int):
        self._capacity = max(1, capacity)
        self._map: Dict[K, tuple[V, DListNode[K]]] = {}
        self._head: Optional[DListNode[K]] = None  # 最近使用
        self._tail: Optional[DListNode[K]] = None  # 最久未使用

    def _unlink(self, node: DListNode[K]) -> None:
        """O(1) 从链中移除节点"""
        if node.prev:
            node.prev.next = node.next
        else:
            self._head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self._tail = node.prev

    def _push_front(self, key: K) -> DListNode[K]:
        """O(1) 插入头部"""
        node = DListNode(key, None, self._head)
        if self._head:
            self._head.prev = node
        else:
            self._tail = node
        self._head = node
        return node

    def _pop_tail(self) -> Optional[K]:
        """O(1) 尾删"""
        if self._tail is None:
            return None
        key = self._tail.value
        self._unlink(self._tail)
        return key

    def get(self, key: K) -> Optional[V]:
        """O(1) 获取并更新访问顺序"""
        if key not in self._map:
            return None
        val, node = self._map[key]
        self._unlink(node)
        new_node = self._push_front(key)
        self._map[key] = (val, new_node)
        return val

    def put(self, key: K, value: V) -> None:
        """O(1) 插入，若存在则更新并移到头部"""
        if key in self._map:
            _, node = self._map[key]
            self._unlink(node)
        elif len(self._map) >= self._capacity:
            evicted = self._pop_tail()
            if evicted is not None:
                self._map.pop(evicted, None)
        new_node = self._push_front(key)
        self._map[key] = (value, new_node)

    def __contains__(self, key: K) -> bool:
        return key in self._map

    def __len__(self) -> int:
        return len(self._map)
>>>>>>> 5509c1398c0685e011f840fcbbe6dd0969d7e3cb
