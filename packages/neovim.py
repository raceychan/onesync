from base import git_clone, cmd

# NOTE: since this is a configurable package, we should make this a Configurable class


def _download_latest_nvim():
    cmd("sudo add-apt-repository -y ppa:neovim-ppa/stable")
    cmd("sudo apt-get update && sudo apt-get install -y neovim")


def _install_chadnvim():
    # install chadnvim
    git_clone("https://github.com/NvChad/NvChad", "~/.config/nvim", depth=1)


def install():
    _download_latest_nvim()
    _install_chadnvim()
