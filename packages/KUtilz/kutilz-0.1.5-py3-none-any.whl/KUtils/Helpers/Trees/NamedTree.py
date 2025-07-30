from KUtils.Typing import *
from queue import Queue
from collections import deque


class NamedTreeMixin:
    name: str
    children: Dict[str, Self] = None
    parent: Self = None

    @property
    def level_order(self) -> List[Self]:
        """Returns a list of nodes in level-order traversal order."""
        result = []
        queue = deque([self])  # Start with the root node

        while not len(queue) == 0:
            current = queue.popleft()
            result.append(current)

            queue.extend(current.children.values())

            # Enqueue children in dictionary order
            # if current.children:
            #     for child in sorted(current.children.values(), key=lambda x: x.name):
            #         queue.append(child)

        return result

    def add_child(self, other: Self) -> None:
        self.children = self.children or {}
        self.children[other.name] = other