from pathlib import Path
from dataclasses import dataclass

from onesync.config import Settings
from onesync.base import shell, Configurable, logger
from onesync.gitools import git_clone, NONE_SENTINEL


async def set_as_default():
    """
    NOTE: this method requires an updated version of cmd
    since it requires user input for password
    """
    await shell("chsh -s $(which zsh)")


@dataclass
class ZSH(Configurable):
    _is_installed: bool = False

    root_dir: Path = Path.home() / ".zsh"
    as_default: bool = True

    @classmethod
    def from_settings(cls, settings: Settings):
        # This should be generalized, config path can be built with pattern
        # TODO: remove, packages should not need to be instantiated
        return cls(
            config_path=settings.zsh.CONFIG_PATH,  # type: ignore
            onedrive_config=settings.zsh.ONEDRIVE_CONFIG,  # type: ignore
        )

    @property
    def is_installed(self) -> bool:
        if Path("/usr/bin/zsh").exists():
            logger.info(f"{self.name} is already installed")
            self._is_installed = True
        return self._is_installed

    @property
    def plugins_dir(self) -> Path:
        return self.root_dir / "zsh-plugins"

    # install conda and python environment
    async def install_p10k(self):
        path = self.plugins_dir / "powerlevel10k"
        if not path.exists():
            await git_clone(
                "https://github.com/romkatv/powerlevel10k.git", path, depth=1
            )
            await shell(f"""echo 'source {path}/powerlevel10k.zsh-theme' >>~/.zshrc""")

    async def install_zsh_nord(self):
        path = self.plugins_dir / "zsh-dircolors-nord"
        if not path.exists():
            await git_clone(
                "https://github.com/coltondick/zsh-dircolors-nord.git",
                path,
                recursive=NONE_SENTINEL,
            )
            await shell(f"source {path}/zsh-dircolors-nord.zsh")

    async def install_zsh_autosuggestion(self):
        path = self.plugins_dir / "zsh-autosuggestions"
        if not path.exists():
            await git_clone("https://github.com/zsh-users/zsh-autosuggestions", path)
            await shell(f"source {str(path)}/zsh-autosuggestions.zsh")

    async def install_synx_highlighting(self):
        path = self.plugins_dir / "zsh-syntax-highlighting"
        if not path.exists():
            await git_clone(
                "https://github.com/zsh-users/zsh-syntax-highlighting.git", path
            )
            await shell(f"source {str(path)}/zsh-syntax-highlighting.zsh")

    async def install_autojump(self):
        path = self.plugins_dir / "autojump"
        if not path.exists():
            await git_clone("git@github.com:wting/autojump.git", str(path))
            install_py = path / "install.py"
            await shell(f"cd {str(path)} && python {str(install_py)}")

    async def install_plugins(self):
        """
        most popular zsh plugins
        https://safjan.com/top-popular-zsh-plugins-on-github-2023/
        """

        # TODO: rewrite this, accept a list of plugins
        logger.info(f"installing {self.name} plugins")
        self.plugins_dir.mkdir(exist_ok=True, parents=True)

        await self.install_p10k()
        await self.install_autojump()
        await self.install_zsh_nord()
        await self.install_zsh_autosuggestion()
        await self.install_synx_highlighting()

    async def install_self(self):
        # apt.install("zsh", y)
        await shell("sudo apt install -y zsh")

    async def install(self):
        if self.is_installed:
            logger.info("zsh is already installed in current system")
            return

        await self.install_plugins()
        await self.install_self()

        self.sync_conf()

        if self.as_default and not self.is_default_shell:
            # sh_path = Path(__file__).parent / "set_as_default.sh"
            logger.warning(f"{self.name} is not default shell")
            await set_as_default()

    @property
    async def is_default_shell(self):
        res = await shell("ps -p $$ | awk 'FNR == 2 {print $4}'")
        return res and res.stdout.strip() == self.name
