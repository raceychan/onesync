# from base import load_toml
from onesync.installer import apt_install
from onesync.base import Package


def make_package(name):
    return type(name, (Package,), {})


# TODO: read from dependency.toml
apt_pkgs = ["zsh", "curl", "ncdu", "git", "iproute2", "python3-pip", "ripgrep", "tmux"]

apt_enhanced_pkgs = [
    "httpie",
    "exa",
    "neovim",
    "bat",
    "btop",
    "net-tools",
    "fd",
    "fzf",
    "ranger",
    "tree",
]

apt_packages_optional = [
    "gnupg",
    "jq",
    "pass",
    "pwgen",
    "rsync",
    "shellcheck",
    "unzip",
]

# NOTE: some of these packages needs extra care
# e.g: exa can't be installed natively in Ubuntu 20


async def install():
    """
    # TODO: install all sub-packages of zsh within a same function. better abstraction needed

    #dependencies.toml
    [zsh.plugins]
    auto-suggestion=...

    for plugin in self.plugins:
        self.install_plugins(plugin)
    """
    pkgs = apt_pkgs + apt_enhanced_pkgs
    await apt_install(pkgs)
