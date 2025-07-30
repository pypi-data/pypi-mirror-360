import time

from .CacheMan import CacheMan
from ..Mixins.BaseMixin import BaseMixin
from KUtils.Typing import *

class VersionedCachedMixin:
    _cache: CacheMan

    @classmethod
    def get_version_managed_key(cls) -> str:
        return cls.__name__ + 'version_managed_k'

    def compute_version(self) -> str:
        return str(time.time())

    @classmethod
    def __read_version(cls, cacheman: CacheMan) -> str:
        vkey = cacheman.get(
            f'{cls.get_version_managed_key()}/version_k', default=None
        )
        return vkey
        # print(f'Retrieved version key {vkey}')

    def __set_version(self, version: str) -> str:
        self._cache.put(
            f'{self.__class__.get_version_managed_key()}/version_k',
            version
        )
        # print(f'Saved version key {version}')

    def versioned_save(self) -> None:
        ver = self.compute_version()
        self.__set_version(ver)
        cache_backup = self._cache
        self._cache = None
        cache_backup.put(self.get_version_managed_key(), self, lockphrase=ver)
        self._cache = cache_backup

    @classmethod
    def versioned_load(cls, cacheman: CacheMan) -> Self:
        ver = cls.__read_version(cacheman)
        if ver is None:
            return None

        res = cacheman.typed_get(
                            cls.get_version_managed_key(),
                            lockphrase=ver,
                            type=cls
        )
        return res