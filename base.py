import os
import logging
from subprocess import run, CompletedProcess, PIPE, CalledProcessError
from pathlib import Path
from typing import Union, Final

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__file__)

# from asyncio.subprocess import create_subprocess_exec, create_subprocess_shell, Process

NONE_SENTINEL: Final = object()

def cmd(*args, timeout=60, shell=True, check=True, text=True, **kwargs) -> CompletedProcess | None:
    try:
        cp = run(*args, timeout=timeout, shell=shell, check=check, text=text, stdout=PIPE, stderr=PIPE, **kwargs)
    except CalledProcessError as ce:
        print(ce.stderr)
        print(f'Failed to execute {args}')
    else:
        if isinstance(cp.stdout, str):
            print(cp.stdout)
        return cp 

def _ssh_to_https(url: str) -> str:
    if url.startswith("git@github.com:"):
        return url.replace("git@github.com:", "https://github.com/")
    return url

def _build_git_command(target: str, local: Union[str, Path], https: bool = True, **kwargs) -> str:
    if https:
        target = _ssh_to_https(target)

    extra = ''
    if kwargs:
        for k,v in kwargs.items():

            if v is not NONE_SENTINEL:
                phrase = f' --{k}={v}'
            else:
                phrase = f' --{k}'
            extra += phrase

    git = f"git clone{extra} {target} {str(local)}"
    return git


def git_clone(url: str, path: str | Path, https: bool=True,  **kwargs):
    if Path(path).exists():
        logger.warning('target path already exists')    
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
