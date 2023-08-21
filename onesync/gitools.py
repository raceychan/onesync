from typing import Union, Final
from pathlib import Path
from loguru import logger

from onesync.base import shell


NONE_SENTINEL: Final = object()


def _ssh_to_https(url: str) -> str:
    if url.startswith("git@github.com:"):
        return url.replace("git@github.com:", "https://github.com/")
    return url


def _build_git_command(
    target: str, local: Union[str, Path], https: bool = True, **kwargs
) -> str:
    if https:
        target = _ssh_to_https(target)

    extra = ""
    if kwargs:
        for k, v in kwargs.items():
            if v is not NONE_SENTINEL:
                phrase = f" --{k}={v}"
            else:
                phrase = f" --{k}"
            extra += phrase

    git = f"git clone{extra} {target} {str(local)}"
    return git


async def git_clone(url: str, path: str | Path, https: bool = True, **kwargs):
    if Path(path).exists():
        logger.warning("target path already exists")
        return

    git = _build_git_command(url, path, https, **kwargs)
    await shell(git)
    return path


class Git:
    def __init__(self, source="github.com"):
        self.source = source
        self.ssh_url = f"git@{source}"
        self.https_url = f"https://{source}"

    def command(self, cmd, **kwargs):
        extra = ""
        if kwargs:
            for k, v in kwargs.items():
                if v is not NONE_SENTINEL:
                    phrase = f" --{k}={v}"
                else:
                    phrase = f" --{k}"
                extra += phrase

        return f"{cmd}{extra}"

    def clone(
        self, target: str, local: Union[str, Path], https: bool = True, **kwargs
    ) -> str:
        if https:
            target = _ssh_to_https(target)

        cmd = self.command("git clone", **kwargs)
        git = f"{cmd} {target} {str(local)}"
        return git
