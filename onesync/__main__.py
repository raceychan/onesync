import asyncio
import sys
from typer import Typer as Cli, Argument
from typing import Annotated
from onesync import service


from onesync.tui.tui import OneSync

cli = Cli()
tui = OneSync()


@cli.command(no_args_is_help=True)
def install(
    mod_name: Annotated[str, Argument(help="the name of pacakge you want to install")]
):
    """
    accepts mod_name as argument, install the corresponding module.
    if multiple modules with the same name is found, only the first one would be installed.

    Examples
    --------
    ...
    """
    asyncio.run(service.install(mod_name, None))


@cli.command(no_args_is_help=True)
def sync(
    mod_name: Annotated[
        str, Argument(help="the name of pacakge whom config file you want to sync")
    ]
):
    """
    accepts mod_name as argument, synchronizing the correspoding config file of the module
    unless package is expecified, if multiple modules with the same name is found, only the first one would be installed.

    Examples
    --------
    ...
    """

    asyncio.run(service.sync(mod_name, None))


def main():
    tui.run() if len((args := sys.argv)) <= 1 else cli()


if __name__ == "__main__":
    main()
