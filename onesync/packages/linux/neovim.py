import asyncio
from pathlib import Path
from typing import Type

from onesync.base import shell, Configurable, dataclass
from onesync.gitools import git_clone
from onesync.config import SettingBase


# NOTE: since this is a configurable package, we should make this a Configurable class
async def enable_copy():
    await shell("sudo apt install xsel")


async def add_py_support():
    await shell("pip install pynvim")


async def _download_latest_nvim():
    await shell("sudo add-apt-repository -y ppa:neovim-ppa/stable")
    await shell("sudo apt-get update && sudo apt-get install -y neovim")


@dataclass
class NeoVim(Configurable):
    pass

    @classmethod
    async def install(cls):
        await _download_latest_nvim()

    @classmethod
    def from_settings(cls: Type[Configurable], settings: SettingBase) -> Configurable:
        return cls(  # type: ignore
            config_path=Path.home() / ".config/nvim",
            onedrive_config=settings.ONEDRIVE_CONFIG,
        )


@dataclass
class NvChad(NeoVim):
    @classmethod
    async def install(cls):
        await git_clone("https://github.com/NvChad/NvChad", "~/.config/nvim", depth=1)


class LazyVim(NeoVim):
    @classmethod
    async def install(cls):
        await cls._backup_config()

        await shell("git clone https://github.com/LazyVim/starter ~/.config/nvim")
        await shell("rm -rf ~/.config/nvim/.git")

    @classmethod
    async def _backup_config(cls):
        from onesync.base import Command

        cmds = [
            # required
            Command("mv ~/.config/nvim ~/.config/nvim.bak"),
            # optional but recommended
            Command("mv ~/.local/share/nvim ~/.local/share/nvim.bak"),
            Command("mv ~/.local/state/nvim ~/.local/state/nvim.bak"),
            Command("mv ~/.cache/nvim ~/.cache/nvim.bak"),
        ]
        tasks = set()
        for cmd in cmds:

            tasks.add(asyncio.create_task(shell(str(cmd))))

        
        await asyncio.gather(*tasks)
        # await shell(*cmds)


async def install():
    # _download_latest_nvim()
    await LazyVim.install()
