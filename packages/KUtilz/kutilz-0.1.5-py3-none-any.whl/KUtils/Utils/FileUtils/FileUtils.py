import os
import shutil
from os.path import join as pjoin
import json
from KUtils.Typing import *
import pickle
from PIL import Image
import numpy as np
import yaml
from ..ListUtils import ListUtils as liu
from pathlib import Path
from KUtils.Typing import *

_COMMON_IMAGE_EXTS=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp", "svg"]

basename = os.path.basename
exists = os.path.exists
cp = shutil.copy

def all_files(dir: PathLike, exts: Union[List[str], str])->List[str]:
    if isinstance(exts, str):
        exts = [exts]
    # Initialize an empty list to store the results
    files = []

    # Ensure the directory path is valid
    if os.path.exists(dir):
        # Walk through all files and directories in the specified directory
        for root, _, filenames in os.walk(dir):
            for filename in filenames:
                # Check if the file has one of the specified extensions
                if any(filename.endswith(ext) for ext in exts):
                    # Create the full file path and append to the list
                    files.append(os.path.join(root, filename))
    else:
        raise FileNotFoundError(f"Directory '{dir}' does not exist.")

    return files

def jsons_in(dir: PathLike)->List[str]:
    return all_files(dir, ['json'])

def pickles_in(dir: str)->List[str]:
    return all_files(dir, ['pkl'])

def json_read(path: PathLike)->dict:
    with open(path, 'r') as file:
        return json.load(file)

def json_write(j: Any, path: PathLike, **kwargs)->None:
    path = Path(path).with_suffix('.json')
    kwargs.setdefault('indent', 2)
    with open(path, 'w') as file:
        json.dump(j, file, **kwargs)

def yaml_write(y: Any, path: PathLike)->None:
    path = Path(path).with_suffix('.yaml')
    with open(path, 'w') as f:
        yaml.dump(y, f)

def yaml_read(path: PathLike)->Any:
    with open(path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise
        
def lines_read(path: PathLike) -> List[str]:
    with open(path, 'r') as stream:
        return stream.read().splitlines()

def lines_write(lines: Iterable[str], path: PathLike) -> None:
    with open(path, 'w') as stream:
        stream.writelines('\n'.join(lines))

def home_path(addon: str)->str:
    return pjoin(os.path.expanduser('~'), addon)

def pickle_write(obj: Any, path: PathLike)->None:
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

def pickle_read(path: PathLike)->Any:
    with open(path, 'rb') as f:
        return pickle.load(f)

def imread(path: PathLike)->np.ndarray:
    img = Image.open(path)
    return np.asarray(img)

def ext(filename: PathLike)->str:
    filename = str(filename)
    return filename[liu.last_index(filename, '.') + 1:]

def filename_no_ext(filename: PathLike)->str:
    filename = str(filename)
    return filename[:liu.last_index(filename, '.')]

def unique_filenames(path: PathLike, absolute: bool = False)->List[str]:
    files = os.listdir(path)
    names = list(set([filename_no_ext(file) for file in files]))
    if not absolute:
        return names
    else:
        return [os.path.join(path, name) for name in names]

def guess_image_format(dir_path: PathLike)->str:
    files = os.listdir(dir_path)
    extents = list(set([ext(file) for file in files]))
    assert len(extents) <= 2, f'Currently only supporting directories with 2 file types, '

    extents = [extent for extent in extents if extent in _COMMON_IMAGE_EXTS]
    assert len(extents) == 1

    return extents[0]

def force_abs(path: PathLike, default_dir: PathLike = None)->str:
    if path.startswith('~'):
        path = Path(path).expanduser()
    else:
        path = Path(path)
    
    if not path.is_absolute():
        default_dir = default_dir or os.getcwd()
        path = Path(default_dir, path)

    return str(path)

def ls(path: Union[str, Path], absolute: bool = True)->List[str]:
    items = os.listdir(path)
    if absolute:
        items = [Path(path, item).__str__() for item in items]
    return items

def force_mkdirs(path: PathLike)->None:
    os.makedirs(path, exist_ok=True)

def rm_dir(path: PathLike)->None:
    os.rmdir(path)

def rm(path: Path, exist_ok: bool = False) -> None:
    try:
        # Check if the path is a symlink
        if path.is_symlink():
            path.unlink()  # Remove the symlink
        # Check if the path is a file
        elif path.is_file():
            path.unlink()  # Remove the file
        # Check if the path is a directory
        elif path.is_dir():
            shutil.rmtree(path)  # Remove directory and its contents recursively
        else:
            print(f"Unknown path type: {path}")
    except FileNotFoundError as e:
        if exist_ok:
            return
        else:
            raise e
    except PermissionError:
        print(f"Permission denied: {path}")
    except OSError as e:
        print(f"Error removing {path}: {e}")

def rm_from_dir(path: PathLike)->None:
    path = Path(path)
    for item in path.glob('*'):
        rm(item)

def write_one(path: PathLike, content: str, force=False)->None:
    assert force or os.path.exists(path), f'Set force if you want to override {path}'
    with open(path, 'w') as f:
        f.write(content)

def symlink(src: str, dest: str, overwrites=False)->None:
    try:
        os.symlink(src, dest)
    except FileExistsError as e:
        if not overwrites:
            raise e
        else:
            os.remove(dest)
            os.symlink(src, dest)

def mv(src: str, dest: str) -> None:
    shutil.move(str(src), str(dest))

def base_name_no_ext(path: PathLike)->str:
    return basename(filename_no_ext(path))

def change_file_base_name_no_ext(path: PathLike, new_name: str)->str:
    file_basename = base_name_no_ext(path)
    return Path(str(path).replace(file_basename, new_name))

def change_ext(path: PathLike, target_ext: str)->Path:
    str_p = str(path)
    str_p = str_p.replace(
        ext(str_p), target_ext
    )
    return Path(str_p)

def dirs_in(path: PathLike)->List[Path]:
    path = Path(path)
    items = path.glob('*')
    return [item for item in items if item.is_dir()]

def named_dirs(path: Path)->Dict[str, Path]:
    dirs = dirs_in(path)
    return {
        direc.name: direc for direc in dirs
    }

def descend_til_non_trivial(path: Path) -> Path:
    # assert path.exists()
    children = list(path.glob('*'))
    if len(children) == 1 and children[0].is_dir():
        return descend_til_non_trivial(children[0])
    else:
        return path

def time_sorted(root: PathLike, pattern: str = '*') -> List[Path]:
    root = Path(root)
    files = root.glob(pattern)
    return sorted(files, key=os.path.getctime)

def latest_in(root: PathLike, pattern: str = '*') -> Path:
    return time_sorted(root, pattern)[-1]