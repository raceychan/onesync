from onesync.importer import import_package, import_configurable
from onesync.shell import shell_factory
from onesync.installer import load_installation

# NOTE: param package should be removed in both method


async def install(mod_name: str, package: None):
    mod = import_package(mod_name, package)
    # should this be: apt.install(mod) ?
    shell = shell_factory()

    coro = shell("ls")

    """
    shell = Shell(package_tool=APT())
    await shell.install(mod)
    """


async def sync(mod_name: str, package: None):
    # TODO: when sync, compare diff using
    # git diff [<options>] --no-index [--] <path> <path>
    # reff: https://stackoverflow.com/questions/16683121/git-diff-between-two-different-files
    # https://github.com/gitpython-developers/GitPython/tree/main

    # BUG: any module can be imported, instead of configurable ones only
    mod = import_configurable(mod_name, package)
