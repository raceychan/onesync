from pathlib import Path
from types import ModuleType
from importlib import import_module as raw_import_module
from erros import ModuleNotFoundError


IGNORED_DIR = {".ipynb_checkpoints", "__pycache__"}


def as_importable(pypath: str | Path):
    return str(pypath).replace("/", ".")[:-3]


def import_module(name: str | Path, package=None) -> ModuleType:
    if isinstance(name, Path):
        importable = as_importable(name)
        mod = raw_import_module(importable, package)
    else:
        mod = raw_import_module(name, package)
    return mod


def is_py_module(f: Path, exclude_init=True) -> bool:
    f_name = f.name
    if not f.is_file():
        return False
    if exclude_init and f_name == "__init__.py":
        return False
    return f_name[-3:] == ".py"


def get_submodules(package_dir: Path) -> list[Path]:
    """
    list all sub-modules of a given package dir, return them in a list of absolute path
    """
    files = []
    for f in package_dir.iterdir():
        if f.is_dir():
            if f.name in IGNORED_DIR:
                continue
            files.extend(get_submodules(f))
        elif is_py_module(f):
            files.append(f)
        else:
            continue
    return files


def get_relative_submodules(package: Path) -> list[Path]:
    current_dir = Path.cwd()  # return caller's path
    sub_mods = [mod.relative_to(current_dir) for mod in get_submodules(package)]
    return sub_mods


def import_submodules(package: Path) -> None:
    for mod in get_relative_submodules(package):
        import_module(mod)


def search_module(mod_name: str, package=Path.cwd()) -> Path:
    sub_mods = get_relative_submodules(package)
    for mod in sub_mods:
        if as_importable(mod.name) == mod_name:
            return mod
    else:
        raise ModuleNotFoundError
