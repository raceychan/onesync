from base import shell, Configurable, git_clone, NONE_SENTINEL, logger
from pathlib import Path
from config import Settings


def set_as_default():
    """
    NOTE: this method requires an updated version of cmd
    since it requires user input for password
    """
    shell("chsh -s $(which zsh)")


class ZSH(Configurable):
    def __init__(
        self,
        *,
        config_file: Path,
        onedrive_config: Path,
        root_dir: Path = Path.home() / ".zsh",
        as_default: bool = True,
    ):
        super().__init__(config_file=config_file, onedrive_config=onedrive_config)
        self.root_dir = root_dir
        self.as_default = as_default
        self._is_installed = False

    @classmethod
    def from_settings(cls, settings: Settings):
        # This should be generalized, config path can be built with pattern
        # TODO: remove, packages should not need to be instantiated
        return cls(
            config_file=settings.zsh.CONFIG_FILE,
            onedrive_config=settings.zsh.ONEDRIVE_CONFIG,
        )

    @property
    def is_installed(self) -> bool:
        return self._is_installed

    @property
    def plugins_dir(self) -> Path:
        return self.root_dir / "zsh-plugins"

    # install conda and python environment
    def install_p10k(self):
        path = self.plugins_dir / "powerlevel10k"
        if not path.exists():
            git_clone("https://github.com/romkatv/powerlevel10k.git", path, depth=1)
            shell(f"""echo 'source {path}/powerlevel10k.zsh-theme' >>~/.zshrc""")

    def install_zsh_nord(self):
        path = self.plugins_dir / "zsh-dircolors-nord"
        if not path.exists():
            git_clone(
                "https://github.com/coltondick/zsh-dircolors-nord.git",
                path,
                recursive=NONE_SENTINEL,
            )
            shell(f"source {path}/zsh-dircolors-nord.zsh")

    def install_zsh_autosuggestion(self):
        path = self.plugins_dir / "zsh-autosuggestions"
        if not path.exists():
            git_clone("https://github.com/zsh-users/zsh-autosuggestions", path)
            shell(f"source {str(path)}/zsh-autosuggestions.zsh")

    def install_synx_highlighting(self):
        path = self.plugins_dir / "zsh-syntax-highlighting"
        if not path.exists():
            git_clone("https://github.com/zsh-users/zsh-syntax-highlighting.git", path)
            shell(f"source {str(path)}/zsh-syntax-highlighting.zsh")

    def install_autojump(self):
        path = self.plugins_dir / "autojump"
        if not path.exists():
            git_clone("git@github.com:wting/autojump.git", str(path))
            install_py = path / "install.py"
            shell(f"cd {str(path)} && python {str(install_py)}")

    def install_plugins(self):
        """
        most popular zsh plugins
        https://safjan.com/top-popular-zsh-plugins-on-github-2023/
        """

        # TODO: rewrite this, accept a list of plugins
        logger.info(f"installing {self.name} plugins")
        self.plugins_dir.mkdir(exist_ok=True, parents=True)

        self.install_p10k()
        self.install_autojump()
        self.install_zsh_nord()
        self.install_zsh_autosuggestion()
        self.install_synx_highlighting()

    def install(self):
        self.install_plugins()
        self.sync_conf()

        if self.as_default and not self.is_default_shell:
            # sh_path = Path(__file__).parent / "set_as_default.sh"
            logger.warning(f"{self.name} is not default shell")

        self._is_installed = True

    @property
    def is_default_shell(self):
        res = shell("ps -p $$ | awk 'FNR == 2 {print $4}'")
        return res and res.stdout.strip() == self.name