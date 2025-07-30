import time
from time import perf_counter_ns as perf_counter
import functools
from typing import TypeVar

__all__ = ['stopwatch']

_Fun = TypeVar('__Fun')

class stopwatch:
    def __init__(self, action_name: str = None, action_str: str = None,  enable: bool = True):
        self.action_str = action_str
        self.action_name = action_name
        self.start = None
        self.enable = enable

    def __enter__(self):
        if self.enable is False:
            return 
        
        self.start = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        if self.enable is False:
            return

        elapsed = float(perf_counter() - self.start) / 1e6

        readout = 'time elapsed for action {} was {:.2f}ms!'.format(
            self.action_name or 'anonymous',
            elapsed
        )
        print(readout)

    def __call__(self, func: _Fun) -> _Fun:
        if self.enable is False:
            return func

        self.action_name = func.__name__
        def wrapper(*args, **kwargs):
            with self:
                res = func(*args, **kwargs)
            return res
        return wrapper



if __name__ == '__main__':
    @stopwatch()
    def shit():
        print('fuck')

    shit()