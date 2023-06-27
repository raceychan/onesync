from typer import Typer as Cli, Argument, Option
from typing import Annotated
from .importer import import_package, import_configurable

cli = Cli()


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
    # BUG: any module can be imported, instead of configurable ones only
    mod.sync_conf()


# @cli.callback()
# def tui():
#     from tui.tui import OneSync

#     app = OneSync()
#     app.run()


if __name__ == "__main__":
    cli()
