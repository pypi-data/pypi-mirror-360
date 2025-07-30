from KUtils.Typing import *

class ILogger(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self._buf = ''

    def line(self, content: str) -> None:
        self._buf += content
        self._buf += '\n'
        self.flush()

    def block(self, title: str, sperator: str = '='):
        class BlockCtx:
            def __init__(self, logger):
                self.logger = logger
                self.start = len(logger._buf)
            def __enter__(self):
                self.logger._buf += f"{title}\n{sperator * len(title)}\n"
                self.logger.flush()
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.logger._buf += f"{sperator * len(title)}\n"
                self.logger.flush()
        return BlockCtx(self)

    @abstractmethod
    def flush(self): ...