import typer
from importer import import_module, search_module

cli = typer.Typer()


@cli.command()
def install(mod_name: str):
    """
    The default entry point of the program.
    accepts mod_name as argument, install the corresponding module.
    if multiple modules with the same name is found, only the first one would be installed.
    """

    mod = import_module(search_module(mod_name))
    mod.install()


@cli.command()
def sync(mod_name: str = ""):
    print("syncing dotfiles")


def main():
    cli()


if __name__ == "__main__":
    main()
