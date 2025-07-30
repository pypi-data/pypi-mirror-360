import inspect
from KUtils import StringUtils as stru
from KUtils.Typing import *

class BoilerplateWriter:
    @classmethod
    def SearchAndReplace(cls, src: Union[object, str], find: str, targets: List[str], match_casing=True)->str:
        res = []

        if not isinstance(src, str):
            src = inspect.getsource(src)

        for target in targets:
            once = src.replace(find, target)
            once = once.replace(find.capitalize(), target.capitalize())
            res.append(once)
            res.append('\n')

        return res