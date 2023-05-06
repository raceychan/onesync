from typer import Typer as Cli, Argument, Option
from typing import Annotated
from importer import ez_import, get_package

# from typing_extensions import Annotated

cli = Cli()


@cli.command(no_args_is_help=True)
def install(
    mod_name: Annotated[str, Argument("", help="the name of pacakge you want to install")],  # type: ignore
    package: Annotated[str, Option("", help="parent package")] = "packages",  # type: ignore
):
    """
    The default entry point of the program.
    accepts mod_name as argument, install the corresponding module.
    if multiple modules with the same name is found, only the first one would be installed.

    Examples
    --------
    pass
    """
    mod = ez_import(mod_name)
    if pkg_clz := get_package(mod.__name__):
        pkg_clz().install()
    else:
        # if not hasattr(mod, "install"):
            # raise NotImplementedError
        try:
            mod.install()
        except AttributeError:
            raise NotImplementedError

@cli.command()
def sync(mod_name: str):
    # NOTE: need to first import before instantiate the class
    mod = ez_import(mod_name)
    if pkg_clz := get_package(mod.__name__):
        pkg_clz().sync_conf()
    else:
        try:
            mod.sync_conf()
        except AttributeError:
            raise NotImplementedError


if __name__ == "__main__":
    cli()
