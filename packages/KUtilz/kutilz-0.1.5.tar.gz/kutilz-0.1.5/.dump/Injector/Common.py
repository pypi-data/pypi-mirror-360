import functools


class MARKERS:
    Injector = '__Injector__'

    # @functools.cache


class PropertyConsumedError(Exception):
    pass
def _CONSUMED(*args, **kwargs): raise PropertyConsumedError()

def get_consumed_func():
    return lambda: _CONSUMED()