from pathlib import Path
from types import ModuleType
from typing import Type
from importlib import import_module as importlib_import
from errors import ModuleNotFoundError
from config import settings
from base import Package, Configurable


def as_importable(pypath: str | Path):
    """
    Examples
    --------
    >>> as_importable("packages/python/jupyter.py")
    ... packages.python.jupyter
    """
    importable = str(pypath).replace("/", ".").removesuffix(".py")
    return importable


def import_module(name: str | Path, package: str | None = None) -> ModuleType:
    """
    A wrapper on importlib.import_module, add a feature which supports module path as input

    Examples
    --------
    import_module(Path("importer.py"))
    """
    importable = as_importable(name)
    mod = importlib_import(importable, package)
    return mod


def is_py_module(f: Path, exclude_init: bool = True) -> bool:
    f_name = f.name
    if not f.is_file():
        return False
    if exclude_init and f_name == "__init__.py":
        return False
    return f_name[-3:] == ".py"


def get_submodules(
    package_dir: Path, skip_dirs: set[str] = settings.IGNORED_DIR
) -> list[Path]:
    """
    list all sub-modules of a given package dir, return them in a list of absolute path
    """
    files = []
    for f in package_dir.iterdir():
        if f.is_dir():
            if f.name in skip_dirs:
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


def search_module(mod_name: str, *, package: Path = Path.cwd()) -> Path:
    """
    return the first module that matches the mod_name
    """
    sub_mods = get_relative_submodules(package)
    for mod in sub_mods:
        if as_importable(mod.name) == mod_name:
            return mod
    else:
        raise ModuleNotFoundError


def ez_import(mod_name: str, package: str | None = None) -> ModuleType:
    """
    NOTE: fix edge cases, eg: raise warning or exception for case
    where there is more than one candidate module
    """
    if package:
        pkg = import_module(search_module(mod_name, package=Path(package)), package)
    else:
        pkg = import_module(search_module(mod_name))
    return pkg


def get_package(mod_name: str) -> Type[Package] | None:
    """
    Given a mod_name, return the registered package from the module
    """
    pkg_clz = Package.registry.get(mod_name)
    return pkg_clz


# NOTE: this method shoud be removed, use get_package directly
# when we solve the Configurable.from_settings issue
def get_configurable(mod_name: str) -> Type[Configurable] | None:
    cfg_clz = Configurable.registry.get(mod_name)
    return cfg_clz


def import_package(mod_name: str, package) -> Package | ModuleType:
    mod = ez_import(mod_name, package)
    if pkg_clz := get_package(mod.__name__):
        if issubclass(pkg_clz, Configurable):
            return pkg_clz.from_settings(settings)
        else:
            return pkg_clz()
    else:
        return mod


def import_configurable(mod_name: str) -> Configurable | ModuleType:
    # TODO: packages should not need to be instantilized,
    # otherwise it would be painful to write more packages
    mod = ez_import(mod_name)
    if pkg_clz := get_configurable(mod.__name__):
        return pkg_clz.from_settings(settings)  # type: ignore
    else:
        return mod
