import tomllib
import yaml
from pathlib import Path


class SettingBase:
    # below should be resolved from env
    ONEDRIVE_ROOT: Path = Path("/mnt/d/OneDrive")
    ONEDRIVE_CONFIG: Path = ONEDRIVE_ROOT / "Config/linux/dotfiles"


class ZSH(SettingBase):
    CONFIG_PATH: Path = Path().home() / ".zshrc"


class Settings(SettingBase):
    IGNORED_DIR: set[str] = {".ipynb_checkpoints", "__pycache__"}
    ACCEPTED_YES: list[str] = ["y", "yes", "Y", "YES"]

    zsh: "ZSH" = ZSH()


def read_dependency(label: str):
    with Path("dependency.toml").open("rb") as f:
        data = tomllib.load(f)
    for l in label.split("."):
        data = data.get(l, {})
    return data.get("dependency")


def safe_load(file: str = "onesync.yaml"):
    with Path(file).open() as f:
        data = yaml.safe_load(f)
    return data


settings = Settings()
