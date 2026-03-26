"""
手写单向链表 (Singly Linked List)
用于 LRU Cache 的访问顺序维护
"""
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class ListNode(Generic[T]):
    """单向链表节点"""
    __slots__ = ("value", "next")

    def __init__(self, value: T, next_node: Optional["ListNode[T]"] = None):
        self.value = value
        self.next: Optional["ListNode[T]"] = next_node


class SinglyLinkedList(Generic[T]):
    """
    手写单向链表
    支持 O(1) 头插、O(1) 尾插、O(1) 头删、O(n) 按值删除
    """

    def __init__(self):
        self._head: Optional[ListNode[T]] = None
        self._tail: Optional[ListNode[T]] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def prepend(self, value: T) -> ListNode[T]:
        """O(1) 头插"""
        node = ListNode(value, self._head)
        self._head = node
        if self._tail is None:
            self._tail = node
        self._size += 1
        return node

    def append(self, value: T) -> ListNode[T]:
        """O(1) 尾插"""
        node = ListNode(value)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1
        return node

    def pop_head(self) -> Optional[T]:
        """O(1) 头删"""
        if self._head is None:
            return None
        val = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return val

    def remove_node(self, node: ListNode[T], prev: Optional[ListNode[T]] = None) -> bool:
        """
        O(1) 删除节点（若已知前驱）
        否则需 O(n) 遍历找前驱
        """
        if prev is not None:
            prev.next = node.next
            if node == self._tail:
                self._tail = prev
            self._size -= 1
            return True
        # 无前驱则遍历
        cur = self._head
        p: Optional[ListNode[T]] = None
        while cur and cur is not node:
            p, cur = cur, cur.next
        if cur is None:
            return False
        if p is None:
            self._head = cur.next
            if self._head is None:
                self._tail = None
        else:
            p.next = cur.next
            if cur == self._tail:
                self._tail = p
        self._size -= 1
        return True

    def pop_tail(self) -> Optional[T]:
        """O(n) 尾删（单向链表需遍历找前驱）"""
        if self._head is None:
            return None
        if self._head == self._tail:
            val = self._head.value
            self._head = self._tail = None
            self._size -= 1
            return val
        cur = self._head
        while cur.next != self._tail:
            cur = cur.next
        val = self._tail.value
        cur.next = None
        self._tail = cur
        self._size -= 1
        return val

    def to_list(self) -> list:
        """转为列表"""
        out = []
        cur = self._head
        while cur:
            out.append(cur.value)
            cur = cur.next
        return out


class DListNode(Generic[T]):
    """双向链表节点（用于 LRU O(1) 淘汰）"""
    __slots__ = ("value", "prev", "next")

    def __init__(self, value: T, prev_node: Optional["DListNode[T]"] = None, next_node: Optional["DListNode[T]"] = None):
        self.value = value
        self.prev: Optional["DListNode[T]"] = prev_node
        self.next: Optional["DListNode[T]"] = next_node
