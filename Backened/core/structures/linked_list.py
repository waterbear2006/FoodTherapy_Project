"""
[Data Structures] 链表
职责：提供单链表和双向链表的实现。
"""


class ListNode:
    """
    单链表节点
    """
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class DListNode:
    """
    双向链表节点
    """
    def __init__(self, val=0, prev=None, next=None):
        self.val = val
        self.prev = prev
        self.next = next


class SinglyLinkedList:
    """
    单链表实现
    """
    def __init__(self):
        self.head = None
    
    def append(self, val):
        """
        在链表末尾添加节点
        """
        new_node = ListNode(val)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def prepend(self, val):
        """
        在链表头部添加节点
        """
        new_node = ListNode(val, self.head)
        self.head = new_node
    
    def delete(self, val):
        """
        删除值为 val 的节点
        """
        if not self.head:
            return
        if self.head.val == val:
            self.head = self.head.next
            return
        current = self.head
        while current.next:
            if current.next.val == val:
                current.next = current.next.next
                return
            current = current.next
    
    def find(self, val):
        """
        查找值为 val 的节点
        """
        current = self.head
        while current:
            if current.val == val:
                return current
            current = current.next
        return None
