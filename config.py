from pathlib import Path


class Settings:
    IGNORED_DIR: set[str] = {".ipynb_checkpoints", "__pycache__"}
    ACCEPTED_YES: list[str] = ["y", "yes", "Y", "YES"]

    # below should be resolved from env
    ONEDRIVE_PATH = Path("/mnt/d/OneDrive")
    ONEDRIVE_DOTFILES = ONEDRIVE_PATH / "Config/linux/dotfiles"


settings = Settings
