from KUtils.Typing import *
from .ILogger import ILogger

class SimpleFileLogger(ILogger):
    def __init__(self, path: PathLike, wipes: bool = False) -> None:
        path = Path(path)
        path = path.with_suffix('.txt')
        self.path = path

        if wipes:
            open(self.path, 'w').close()

        super().__init__(name=path.stem)

    def flush(self) -> None:
        if self._buf:
            with open(self.path, 'a') as f:
                f.write(self._buf)
            self._buf = ''

