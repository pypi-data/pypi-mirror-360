from KUtils.Typing import *
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .UniqueIDGenerator import UniqueIDGenerator

class UniqueIDMixin:
    """
    A mixin that provides unique ID functionality to classes.
    Requires initialize_id() to be called before the id property can be used.
    """

    __id_generator: 'UniqueIDGenerator' = None
    __id: str = None

    def initialize_id(self) -> None:
        """
        Initializes the ID for this instance.
        Must be called before accessing the id property.
        """
        if self.__id is None:
            self.__id = str(self.__id_generator.new())

    @property
    def id(self) -> str:
        """
        The unique ID of this instance.

        Raises:
            RuntimeError: If initialize_id() hasn't been called
        """
        if self.__id is None:
            raise RuntimeError("ID not initialized. Call initialize_id() first.")
        return self.__id

    def __del__(self):
        """When the instance is deleted, recycle its ID"""
        if hasattr(self, '_id') and self.__id is not None:
            self.__id_generator.rmv(self._id)