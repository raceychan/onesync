import os
import shutil
from pathlib import Path
from loguru import logger


def sync_zsh():
    onedrive_dir = os.environ.get("ONEDRIVE_DIR", "/mnt/d/OneDrive")
    dotfiles_dir = Path(onedrive_dir) / "Config/linux/dotfiles"
    
    local_zshrc = Path.home() / ".zshrc"
    remote_zshrc = dotfiles_dir / ".zshrc"
    local_zshrc_copy = Path.home() / "local.zshrc.copy"
    remote_zshrc_copy = dotfiles_dir / "remote.zshrc.copy"

    if not local_zshrc.is_file() and not remote_zshrc.is_file():
        raise FileNotFoundError(
            "No .zshrc file found in both $HOME and dotfiles folder."
        )
    elif not remote_zshrc.is_file():
        logger.info(
            "No .zshrc file found in the dotfiles folder. Syncing local .zshrc to the dotfiles folder."
        )
        shutil.copy(local_zshrc, remote_zshrc)
    elif not local_zshrc.is_file():
        logger.info(
            "No .zshrc file found in the $HOME directory. Syncing .zshrc from the dotfiles folder."
        )
        shutil.copy(remote_zshrc, local_zshrc)
    else:
        local_mtime = local_zshrc.stat().st_mtime
        remote_mtime = remote_zshrc.stat().st_mtime

        if local_mtime > remote_mtime:
            logger.info("Local .zshrc file is newer. Syncing to the dotfiles folder.")
            shutil.copy(remote_zshrc, remote_zshrc_copy)
            shutil.copy(local_zshrc, remote_zshrc)
        else:
            logger.info(
                "Remote .zshrc file is newer or the same. Syncing to the local folder."
            )
            shutil.copy(local_zshrc, local_zshrc_copy)
            shutil.copy(remote_zshrc, local_zshrc)
