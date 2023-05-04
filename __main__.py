from typer import Typer as Cli, Argument, Op

from typing import Annotated
from importer import import_module, search_module

# from typing_extensions import Annotated

cli = Cli()


@cli.command(no_args_is_help=True)
def install(
    mod_name: Annotated[str, Argument(help="the name of pacakge you want to install")],  # type: ignore
    package: Annotated[str, Option(help="parent package")] = "packages",  # type: ignore
):
    """
    The default entry point of the program.
    accepts mod_name as argument, install the corresponding module.
    if multiple modules with the same name is found, only the first one would be installed.

    Examples
    --------
    pass
    """

    mod = import_module(search_module(mod_name))
    mod.install()


@cli.command()
def sync(mod_name: str = ""):
    mod = import_module(search_module(mod_name))
    print("syncing dotfiles")


if __name__ == "__main__":
    cli()
