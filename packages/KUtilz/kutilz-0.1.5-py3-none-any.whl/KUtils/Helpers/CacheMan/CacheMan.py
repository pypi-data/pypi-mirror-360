import shelve
from KUtils.Typing import *

def _is_shelve_or_non_exist(path: Path) -> bool:
    return True

class CacheMan:
    def __init__(self, path: PathLike, name: str = '.shelve'):
        path = Path(path)

        assert _is_shelve_or_non_exist(path)

        path.mkdir(exist_ok=True)

        assert path.is_dir()


        self.__root = path
        self.__base_file = str(self.__root / name)
        self.__hash_file = str(self.__root / f'{name}.hash')


        self.__base_cache = shelve.open(self.__base_file)
        self.__hash_cache = shelve.open(self.__hash_file)

    def put(self,
            key: str,
            val: Any,
            lockphrase: str = None) -> None:
        self.__base_cache[key] = val
        if lockphrase:
            self.__hash_cache[key] = lockphrase

    def get(self,
            key: str,
            lockphrase: str = None,
            type: Type[T] = None,
            default: T = None) -> T:
        if lockphrase and self.__hash_cache.get(key, None) != lockphrase:
            return default
        else:
            return self.__base_cache.get(key, default)

    def typed_get(self,
            key: str,
            lockphrase: str = None,
            type: Type[T] = None,
            default: T = None) -> T:
        if lockphrase and self.__hash_cache.get(key, None) != lockphrase:
            return default
        else:
            res = self.__base_cache.get(key, default)
            if res is default:
                return default
            if not isinstance(res, type):
                raise TypeError(f'Retrieved object {res} type mismatch {type}')
            return res


    def __del__(self):
        self.__base_cache.close()
        self.__hash_cache.close()


