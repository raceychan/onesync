from pathlib import Path


class SettingBase:
    # below should be resolved from env
    ONEDRIVE_PATH: Path = Path("/mnt/d/OneDrive")
    ONEDRIVE_CONFIG: Path = ONEDRIVE_PATH / "Config/linux/dotfiles"


class ZSH(SettingBase):
    CONFIG_FILE: Path = Path().home() / ".zshrc"


class Settings(SettingBase):
    IGNORED_DIR: set[str] = {".ipynb_checkpoints", "__pycache__"}
    ACCEPTED_YES: list[str] = ["y", "yes", "Y", "YES"]

    zsh: "ZSH" = ZSH()


settings = Settings
