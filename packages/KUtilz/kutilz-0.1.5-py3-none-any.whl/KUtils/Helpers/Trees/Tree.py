from __future__ import annotations
from KUtils.Typing import *

class TreeNodeMixin:
    __children = None
    __parent = None

    @property
    def children(self) -> List[Self]:
        if self.__children is None:
            self.__children = []
        return self.__children

    @property
    def descendents(self) -> List[Self]:
        all = []

        for child in self.children:
            all.extend([
                child, *child.descendents
            ])

        return all

    @property
    def parent(self) -> Self | None:
        return self.__parent

    def orphanize(self) -> None:
        if self.__parent is not None:
            self.__parent.children.remove(self)

        self.__parent = None

    def clear_children(self) -> None:
        for child in self.children:
            child.orphanize()

    def __compatible(self, other) -> bool:
        return isinstance(other, TreeNodeMixin)

    def __lshift__(self, *other: Self):
        for item in other:
            assert self.__compatible(item), f'{type(item)} is incompatible with TreeNode type {type(self)}'

            if item.__parent is self:
                continue

            item.orphanize()

            item.__parent = self

            self.children.append(item)

    @classmethod
    def ChildNode(cls):
        def decs(fn):
            name = fn.__name__

            name = '_node_prop_' + name

            def fget(self):
                return getattr(self, name)

            def fset(self, val):
                self << val
                object.__setattr__(self, name, val)

            def fdel(self):
                fget(self).orphanize()

            return property(
                fget, fset, fdel
            )

        return decs

    # @classmethod
    # def ChildNodes(cls):
    #     def decs(fn):
    #         pass

