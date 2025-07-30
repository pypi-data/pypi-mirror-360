from KUtils.Typing import *

def assemble_vars(vars: Dict[str, str], one_line: bool = True) -> str:
    def handle_v(v: Any) -> str:
        if v is None:
            return 'null'
        else:
            return str(v)

    joiner = '' if one_line else '\n'

    return joiner.join(
        ['[{}:{}]'.format(
            k, handle_v(v)
        ) for k, v in vars.items()]
    )
