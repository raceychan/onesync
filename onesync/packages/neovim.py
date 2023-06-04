from base import git_clone, shell, Configurable

# NOTE: since this is a configurable package, we should make this a Configurable class


class NvChad:
    @classmethod
    def install(cls):
        git_clone("https://github.com/NvChad/NvChad", "~/.config/nvim", depth=1)


class LazyVim:
    @classmethod
    def install(cls):
        cls._backup_config()
        shell("git clone https://github.com/LazyVim/starter ~/.config/nvim")
        shell("rm -rf ~/.config/nvim/.git")

    @classmethod
    def _backup_config(cls):
        cmds = [
            # required
            "mv ~/.config/nvim ~/.config/nvim.bak",

            # optional but recommended
            "mv ~/.local/share/nvim ~/.local/share/nvim.bak",
            "mv ~/.local/state/nvim ~/.local/state/nvim.bak",
            "mv ~/.cache/nvim ~/.cache/nvim.bak",
        ]
        for cmd in cmds:
            shell(cmd)


def _download_latest_nvim():
    shell("sudo add-apt-repository -y ppa:neovim-ppa/stable")
    shell("sudo apt-get update && sudo apt-get install -y neovim")


def install():
    # _download_latest_nvim()
    LazyVim.install()
