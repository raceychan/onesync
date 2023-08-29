from pathlib import Path
from onesync.importer import (
    import_package,
    import_configurable,
    get_submodules,
    as_importable,
)
from onesync.shell import shell_factory, Shell
from onesync.installer import load_installation


def list_modules(module_path: str | Path = "onesync/packages"):
    mods = get_submodules(Path(module_path))
    for module in mods:
        yield as_importable(module.name)


async def install(mod_name: str):
    breakpoint()
    mod = import_package(mod_name, None)

    # apt = APT(shell=shell, mod=mod)
    # await apt.install()

    # onesync.install(tool=apt, mod=mod)

    shell = shell_factory()

    await shell.install(mod)

    """
    shell = Shell(package_tool=APT())
    await shell.install(mod)
    """

    class Instalation:
        def __init__(self, shell: Shell, module: ...):
            ...


async def sync(mod_name: str):
    # TODO: when sync, compare diff using
    # git diff [<options>] --no-index [--] <path> <path>
    # reff: https://stackoverflow.com/questions/16683121/git-diff-between-two-different-files
    # https://github.com/gitpython-developers/GitPython/tree/main

    # BUG: any module can be imported, instead of configurable ones only
    mod = import_configurable(mod_name, None)
    mod.sync_conf()
