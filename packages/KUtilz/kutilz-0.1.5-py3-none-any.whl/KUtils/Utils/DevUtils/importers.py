import types
import importlib.util
import sys
from pathlib import Path
from KUtils.Typing import *
from typing import Dict

__all__ = ['import_folder']

def import_folder(path: Union[Path, str], package = True) -> Dict[str, types.ModuleType]:
    path = Path(path)
    
    if package is True:
        package = path.stem

    modules = {}
    path = path.resolve()
    sys.path.insert(0, str(path.parent))

    for file in path.glob("*.py"):
        if file.name == "__init__.py":
            continue

        module_name = f"{package}.{file.stem}" if package else file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                modules[module_name] = module
                sys.modules[module_name] = module
            except Exception as e:
                raise
                # print(f"[import_folder] Failed to import {file.name}: {e}")
    return modules
