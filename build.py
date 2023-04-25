import typer
import loguru
from importlib import import_module
from base import cmd, ProjectRoot
from packages.zsh.zsh import ZSH
from packages.conda.conda import Conda
from packages import neovim, node, jupyter

cli = typer.Typer()


ACCEPTED_YES = ["y", "yes", "Y", "YES"]

apt_pkgs = ["zsh", "curl", "ncdu", "git", "iproute2", "python3-pip", "ripgrep", "tmux"]

apt_enhanced_pkgs = [
    "httpie",
    "exa",
    "neovim",
    "bat" "btop" "net-tools" "ncdu",
    "fd",
    "fzf",
    "ranger",
    "tree",
]


def continue_after_fail():
    ans = input("Failed to install core packages, do you want to continue? (y/n):")
    return ans in ACCEPTED_YES


# apt_packages_optional=["gnupg", "htop", "jq", "pass", "pwgen", "rsync", "shellcheck", "unzip"]


def apt_install(*packages):
    base_cmd = "sudo apt-get update && sudo apt-get install -y"
    if len(packages) == 1 and isinstance(packages, list):
        pkgs = " ".join(packages[0])
    else:
        pkgs = " ".join(packages)
    print(f"Installing {pkgs}")
    exec_result = cmd(f"{base_cmd} {pkgs}")
    return exec_result


def install_pkgs(pkgs: list[str]):
    pkg_str = " ".join(pkgs)
    install_optional = input(
        "Do you want to install the Following optional packages? (y/n):"
        + "\n"
        + pkg_str
        + "\n"
    )
    if install_optional in ACCEPTED_YES or install_optional == "":
        try:
            apt_install(pkg_str)
        except Exception:
            print("Failed to install optional packages")
    else:
        print("Failed to install packages")


def install_sys_pkgs():
    """
    # TODO: install all sub-packages of zsh within a same function. better abstraction needed

    #dependencies.toml
    [zsh.plugins]
    auto-suggestion=...

    for plugin in self.plugins:
        self.install_plugins(plugin)
    """


def customize_install():
    # init zsh and set it to default shell
    # ZSH().install()

    # install conda and python environment
    # Conda().install()
    # neovim.install()
    # node.install()
    jupyter.install()

@cli.command()
def install(mod_name: str):
    mod = import_module(f"packages.{mod_name}")
    mod.install()


def main():
    install_sys_pkgs()
    customize_install()
    loguru.success("build ends")


if __name__ == "__main__":
    cli()
