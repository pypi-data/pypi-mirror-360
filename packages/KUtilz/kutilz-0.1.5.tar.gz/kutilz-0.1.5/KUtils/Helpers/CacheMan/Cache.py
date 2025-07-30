from KUtils.Typing import *
import shelve
import time

class ICache(ABC):
    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    @abstractmethod
    def set(self, key: str, item: Any, timeout: int = None): pass

    @abstractmethod
    def get(self, key: str, default: Any = None): pass

    @abstractmethod
    def rmv(self, key: str): pass

    @final
    def pop(self, key: str):
        item = self.get(key)
        self.rmv(key)
        return item

    @abstractmethod
    def items(self) -> Iterable[Tuple[str, Any]]: pass
    
    @final
    def try_produce(self, key: str, producer: Callable[[], T]) -> T:
        if self.get(key, None) is None:
            val = producer()
            self.set(key, val)
        return self.get(key)
            

class ShelveCache(ICache):
    def __init__(self, root: str, fname: str):
        root = Path(root)

        assert root.is_dir() and root.exists(), f'{root} is not a valid directory.'

        if '.shelve' not in fname:
            assert '.' not in fname, f'Invalid shelve file name {fname}!'
            fname += '.shelve'
        self.file_path = str(root / fname)


    def set(self, key: str, item: Any, timeout: int = None):
        """
        Store an item in the shelve database. If timeout is not None,
        the item will expire after 'timeout' seconds.
        """
        expire_at = time.time() + timeout if timeout else None
        with shelve.open(self.file_path) as db:
            db[key] = (item, expire_at)

    def get(self, key: str, default: Any = None):
        """
        Retrieve an item by key. If the item has expired or does not exist,
        return default.
        """
        with shelve.open(self.file_path, flag="c") as db:
            if key not in db:
                return default

            value, expire_at = db[key]
            if expire_at is not None and time.time() > expire_at:
                # The cached item has expired; remove it and return default
                del db[key]
                return default

            return value

    def rmv(self, key: str):
        with shelve.open(self.file_path, flag="c") as db:

            if key in db:
                del db[key]
    
    def items(self) -> Iterable[Tuple[str, Any]]:
        with shelve.open(self.file_path, flag="c") as db:
            for key, val in db.items():
                yield key, val[0]