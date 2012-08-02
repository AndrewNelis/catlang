"""
    Basic stack functionality.
"""

from collections import deque


class Stack:

    def __init__(self, initial=None):
        """
            >>> s = Stack()
            >>> s
            _empty_
            >>> s = Stack([1,2,3])
            >>> s
            ===> 1 2 3
        """
        if initial is None:
            initial = []
        self._stack = deque(initial)

    def push(self, what, multi=False):
        """
            >>> s = Stack()
            >>> s.push(1)
            >>> s
            ===> 1
            >>> s.push([2, 3], multi=True)
            >>> s
            ===> 1 2 3
            >>> s.push([4, 5])
            >>> s
            ===> 1 2 3 [4, 5]
        """
        if multi:
            self._stack.extend(what)
        else:
            self._stack.append(what)

    def pop(self):
        """
            >>> s = Stack([1])
            >>> s.pop()
            1
            >>> s
            _empty_
        """
        return self._stack.pop()

    def pop_list(self):
        """
            >>> s = Stack(['a,b,c'])
            >>> s.pop_list()
            ['a', 'b', 'c']
        """
        item = self.pop()

        if isinstance(item, basestring):
            return [x for x in item.split(',') if x]

        elif isinstance(item, (list, tuple)):
            return item

        else:
            raise TypeError('Cannot pop list from top of stack: %r' % item)

    def __repr__(self):
        if not self._stack:
            return '_empty_'

        return '===> %s' % ' '.join(repr(x) for x in self._stack)

    def peek(self):
        """
            >>> s = Stack([1, 2])
            >>> s.peek()
            2
            >>> s
            ===> 1 2
        """
        return self._stack[-1]

    def peek_n(self, n):
        """
            >>> s = Stack([1, 2, 4, 8, 16])
            >>> s.peek_n(3)
            2
        """
        return self._stack[-1 - n]

    def pop_2(self):
        """
            >>> s = Stack([2, 4, 6])
            >>> s.pop_2()
            (6, 4)
        """
        return self._stack.pop(), self._stack.pop()

    def pop_n(self, n):
        """
            >>> s = Stack([3, 4, 5, 6])
            >>> s.pop_n(3)
            [6, 5, 4]
            >>> s
            ===> 3
        """
        return list([self._stack.pop() for _ in range(n)])

    def pop_all(self):
        """
            >>> s = Stack([9, 8, 7])
            >>> s.pop_all()
            [7, 8, 9]
            >>> s
            _empty_
        """
        return self.pop_n(self.length())

    def length(self):
        """
            >>> s = Stack([1, 2, 3])
            >>> s.length()
            3
        """
        return len(self._stack)

    def clear(self):
        """
            >>> s = Stack([20, 30, 40])
            >>> s.clear()
            >>> s
            _empty_
        """
        self._stack.clear()

    def clear_to(self, n):
        """
            >>> s = Stack([90, 40, 10, 1])
            >>> s.clear_to(3)
            >>> s
            ===> 90
        """
        for _ in range(n):
            self._stack.pop()

    def to_list(self):
        return list(self._stack)

    def __getitem__(self, index):
        return self._stack[index]

    def __setitem__(self, index, value):
        self._stack[index] = value
