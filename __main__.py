from typer import Typer as Cli, Argument, Option
from typing import Annotated
from importer import ez_import, get_package

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
    pass
    # if pkg_clz := get_package(mod_name):
    #     pkg_clz.lazy_init().install()
    # else:
    #     ez_import(mod_name).install()


@cli.command()
def sync(mod_name: str):
    # NOTE: need to first import before instantiate the class
    mod = ez_import(mod_name)
    if pkg_clz := get_package(mod.__name__):
        pkg_clz().sync_conf()
    else:
        if hasattr(mod, "sync_conf"):
            mod.sync_conf()
        else:
            raise NotImplementedError


if __name__ == "__main__":
    cli()
