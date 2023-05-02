from pathlib import Path
from subprocess import PIPE, CalledProcessError, CompletedProcess, run
from typing import Final, Union
from loguru import logger
from tomli import loads as load_toml


NONE_SENTINEL: Final = object()


def cmd(
    *args, timeout=60, shell=True, check=True, text=True, bufsize=-1, **kwargs
) -> CompletedProcess | None:
    try:
        cp = run(
            *args,
            timeout=timeout,
            shell=shell,
            check=check,
            text=text,
            stdout=PIPE,
            stderr=PIPE,
            bufsize=bufsize,
            **kwargs,
        )
    except CalledProcessError as ce:
        print(ce.stderr)
        print(f"Failed to execute {args}")
    else:
        if isinstance(cp.stdout, str):
            print(cp.stdout)
        return cp


def get_sys_number() -> str | None:
    res = cmd("lsb_release -a 2>/dev/null | grep 'Release:' | awk '{print $2}'")
    if res and res.stdout:
        sys_num = res.stdout.strip()
    else:
        sys_num = None
    return sys_num


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


def git_clone(url: str, path: str | Path, https: bool = True, **kwargs):
    if Path(path).exists():
        logger.warning("target path already exists")
        return

    git = _build_git_command(url, path, https, **kwargs)
    cmd(git)
    return path


class Package:
    dependencies: list["str|Package"] = []

    def __init__(self, version: str = "latest"):
        self.version = version

    @property
    def name(self):
        return self.__class__.__name__.lower()

    @property
    def doc(self):
        return self.__class__.__doc__

    def dependency_check(self):
        if not self.dependencies:
            return
        for deps in self.dependencies:
            if not isinstance(deps, Package):
                raise Exception
            deps.build()

    def build(self):
        self.dependency_check()
        self.install()

    def install(self):
        raise NotImplementedError


ProjectRoot = Path.cwd()
