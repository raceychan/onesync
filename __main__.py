from typer import Typer as Cli, Argument, Option
from typing import Annotated
from importer import ez_import, import_package, import_configurable
from config import settings

# from typing_extensions import Annotated

cli = Cli()
# NOTE: avoid too many dependencies, since manually install dependencies before using this installing tool is trivial


@cli.command(no_args_is_help=True)
def install(
    mod_name: Annotated[str, Argument(help="the name of pacakge you want to install")],  # type: ignore
    package: Annotated[str, Option(help="parent package")] = None,  # type: ignore
):
    """
    The default entry point of the program.
    accepts mod_name as argument, install the corresponding module.
    if multiple modules with the same name is found, only the first one would be installed.

    Examples
    --------
    pass
    """
    mod = import_package(mod_name, package)
    mod.install()


@cli.command()
def sync(mod_name: str):
    mod = import_configurable(mod_name)
    mod.sync_conf()


if __name__ == "__main__":
    cli()
