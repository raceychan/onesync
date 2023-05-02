from base import load_toml
from installer import apt_install

# TODO: read from dependency.toml
apt_pkgs = ["zsh", "curl", "ncdu", "git", "iproute2", "python3-pip", "ripgrep", "tmux"]

apt_enhanced_pkgs = [
    "httpie",
    "exa",
    "neovim",
    "bat",
    "btop",
    "net-tools",
    "ncdu",
    "fd",
    "fzf",
    "ranger",
    "tree",
]

apt_packages_optional = [
    "gnupg",
    "htop",
    "jq",
    "pass",
    "pwgen",
    "rsync",
    "shellcheck",
    "unzip",
]


def install_core_pkgs():
    """
    # TODO: install all sub-packages of zsh within a same function. better abstraction needed

    #dependencies.toml
    [zsh.plugins]
    auto-suggestion=...

    for plugin in self.plugins:
        self.install_plugins(plugin)
    """
    pkgs = apt_pkgs + apt_enhanced_pkgs
    apt_install(pkgs)
