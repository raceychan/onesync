from pathlib import Path
from typing import Type

from onesync.base import shell, Configurable, dataclass
from onesync.gitools import git_clone
from onesync.config import SettingBase

# NOTE: since this is a configurable package, we should make this a Configurable class
def enable_copy():
    shell("sudo apt install xsel")

def add_py_support():
    shell("pip install pynvim")

def _download_latest_nvim():
    shell("sudo add-apt-repository -y ppa:neovim-ppa/stable")
    shell("sudo apt-get update && sudo apt-get install -y neovim")

@dataclass
class NeoVim(Configurable):
    pass

    @classmethod
    def install(cls):
        _download_latest_nvim()

    @classmethod
    def from_settings(cls: Type[Configurable], settings: SettingBase) -> Configurable:
        return cls( # type: ignore
            config_path=Path.home() / ".config/nvim",
            onedrive_config=settings.ONEDRIVE_CONFIG,
        )

@dataclass
class NvChad(NeoVim):
    @classmethod
    def install(cls):
        git_clone("https://github.com/NvChad/NvChad", "~/.config/nvim", depth=1)


class LazyVim(NeoVim):
    @classmethod
    def install(cls):
        cls._backup_config()

        shell("git clone https://github.com/LazyVim/starter ~/.config/nvim")
        shell("rm -rf ~/.config/nvim/.git")

    @classmethod
    def _backup_config(cls):
        from ..base import Command

        cmds = [
            # required
            Command("mv ~/.config/nvim ~/.config/nvim.bak"),

            # optional but recommended
            Command("mv ~/.local/share/nvim ~/.local/share/nvim.bak"),
            Command("mv ~/.local/state/nvim ~/.local/state/nvim.bak"),
            Command("mv ~/.cache/nvim ~/.cache/nvim.bak"),
        ]
        shell(*cmds)


def install():
    # _download_latest_nvim()
    LazyVim.install()

