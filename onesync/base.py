import os
import re
import shutil
import hashlib
from pathlib import Path
from subprocess import PIPE, CalledProcessError, CompletedProcess, run
from typing import Final, Union, Type, Any
from abc import ABC, abstractmethod
from functools import cached_property

from loguru import logger

# from tomli import loads as load_toml
from config import SettingBase


NONE_SENTINEL: Final = object()
ProjectRoot = Path.cwd()

StrPath = str | Path


def _reduce_hash(hashlist, hashfunc):
    hasher = hashfunc()
    for hashvalue in sorted(hashlist):
        hasher.update(hashvalue.encode("utf-8"))
    return hasher.hexdigest()


def filehash(filepath: Path):
    hasher = hashlib.md5()
    blocksize = 64 * 1024  # 64kb

    if not os.path.exists(filepath):
        return hasher.hexdigest()

    with open(filepath, "rb") as fp:
        while True:
            data = fp.read(blocksize)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def dirhash(
    dirname,
    excluded_files=[],
    ignore_hidden=False,
    followlinks=False,
    excluded_extensions=[],
    include_paths=False,
):
    hashvalues = []
    for root, dirs, files in os.walk(dirname, topdown=True, followlinks=followlinks):
        if ignore_hidden and re.search(r"/\.", root):
            continue

        dirs.sort()
        files.sort()

        for fname in files:
            if ignore_hidden and fname.startswith("."):
                continue

            if fname.split(".")[-1:][0] in excluded_extensions:
                continue

            if fname in excluded_files:
                continue

            hash_list = filehash(os.path.join(root, fname))

            hashvalues.append(hash_list)

            if include_paths:
                hasher = hashlib.md5()
                # get the resulting relative path into array of elements
                path_list = os.path.relpath(os.path.join(root, fname)).split(os.sep)
                # compute the hash on joined list, removes all os specific separators
                hasher.update("".join(path_list).encode("utf-8"))
                hashvalues.append(hasher.hexdigest())

    return _reduce_hash(hashvalues, hashlib.md5)


def md5sum(path: Path):
    return dirhash(path) if path.is_dir() else filehash(path)


def safe_copy(src: Path, dst: Path, *, follow_symlinks: bool = True) -> Path:
    if not src.exists():
        raise Exception(f"source file {src.name} does not exist")

    if src.stat().st_size == 0:
        raise Exception("Empty file bakcup is not allowed")

    if not dst.parent.exists():
        dst.parent.mkdir(parents=True)
    # dst can be either a file or a dir, either way, the parent would be a dir.

    return shutil.copy(src, dst, follow_symlinks=follow_symlinks)


def shell(
    *args, timeout=60, shell=True, check=True, text=True, bufsize=-1, **kwargs
) -> CompletedProcess | None:
    # NOTE: rewrite needed so that output shows out on screen simutaneously
    logger.info(args)
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
            executable="/usr/bin/zsh",
            **kwargs,
        )
    except CalledProcessError as ce:
        logger.error(ce.stderr)
        logger.info(f"Failed to execute {args}")
    else:
        if isinstance(cp.stdout, str):
            logger.success(cp.stdout)
        return cp


def get_sys_number() -> str | None:
    res = shell("lsb_release -a 2>/dev/null | grep 'Release:' | awk '{print $2}'")
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
    shell(git)
    return path


def _sync_copy_log(filename: str, missed: Path, found: Path):
    msg = f"No {filename} file found in {missed}. Syncing {filename} from {missed} to {found}"
    logger.info(msg)


def are_same_file(*files):
    md5sum(*files)


# provides a convenient way to combine commands, aim to replace multiple shell(command) call
class Command(str):
    def __new__(cls, *args):
        return super().__new__(cls, *args)

    def __add__(self, other):
        return " && ".join((self, other))


class Package(ABC):
    # TODO: make this a dataclass, and this should not require instantiation
    registry: dict[str, Type["Package"]] = dict()

    def __init__(
        self,
        *,
        name: str = "",
        version: str = "latest",
        dependencies: list["str|Package"] = [],
    ):
        self.name = name or self.__class__.__name__.lower()
        self.version = version
        self.dependencies = dependencies

    @classmethod
    def from_settings(cls: Type["Package"], settings: SettingBase):
        """
        factory method to create Package instance using settings
        """
        raise NotImplementedError

    def __init_subclass__(cls) -> None:
        cls.registry[cls.__module__] = cls

    @cached_property
    def doc(self):
        return self.__class__.__doc__

    @abstractmethod
    def install(self):
        """
        customized installing method of the package
        """
        raise NotImplementedError

    @classmethod
    def register(cls, *args, **kwargs):
        """
        A decorator used to register a class as package.

        @Package.register
        class Tmux:
            ...
        """

        class PackageLike:
            def __init__(self, pkg_clz: Type[Any]):
                ...

        def package_cls(pkg_clz: Type[Any]):
            cls.registry[pkg_clz.__module__] = pkg_clz
            return pkg_clz

        if not kwargs and len(args) == 1:
            # case where no args and kwargs were inputed
            ...
        else:
            wrapper = package_cls

        return package_cls

    @classmethod
    def lazy_init(cls, **kwargs):
        return cls(**kwargs)

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


class Configurable(Package):
    # registry: dict[str, Type["Configurable"]] = dict()

    def __init__(self, *, config_path: Path, onedrive_config: Path):
        super().__init__()
        self.config_path = config_path
        self.onedrive_config = onedrive_config

    @classmethod
    def from_settings(cls: Type[Package], settings: SettingBase) -> "Configurable":
        return super().from_settings(settings)

    @cached_property
    def config_filename(self) -> str:
        # NOTE: remove this, use self.config_file.name
        if not self.config_path:
            raise Exception("config_file not set")
        return self.config_path.name

    @cached_property
    def config_copy(self) -> str:
        """
        Return filename in the format of ``"package.config_filename.bak"``
        NOTE: config could be either a dir or a single file

        Examples
        --------

        >>> package = zsh
        >>> config_filname = .zshrc
        >>> config_copy
        ... zsh.zshrc.bak
        """
        if self.config_path.name.startswith("."):
            file_name = f"{self.name}{self.config_path.name}.bak"
        else:
            file_name = f"{self.name}.{self.config_path.name}.bak"
        return file_name

    @cached_property
    def local_copy_path(self) -> Path:
        copy_path = Path.home() / ".config" / "onesync" / "dotfiles"
        local_copy = copy_path / self.config_copy
        return local_copy

    def sync_conf(self):
        """
        generated by GPT, modifications needed for a more generalized version.

        reff: https://techcommunity.microsoft.com/t5/ask-the-directory-services-team/understanding-dfsr-conflict-algorithms-and-do        ing-something-about/ba-p/397346

        File conflict algorithm
        """

        remote_conf = self.onedrive_config / self.config_filename

        if not self.config_path.exists() and not remote_conf.exists():
            raise FileNotFoundError(
                f"No {self.config_filename} file found in both {self.config_path} and {self.onedrive_config}."
            )
        elif not remote_conf.exists():
            _sync_copy_log(self.config_filename, self.onedrive_config, self.config_path)
            shutil.copy(self.config_path, remote_conf)
        elif not self.config_path.exists():
            _sync_copy_log(self.config_filename, self.config_path, self.onedrive_config)
            shutil.copy(remote_conf, self.config_path)
        else:
            self.update_conf()

    def update_conf(self):
        # BUG: this method is not idem, it always sync whether file changed.
        # NOTE: feature: use diff to compare files
        # NOTE: feature: support autosync using watchdog to detech file changes

        remote_conf = self.onedrive_config / self.config_filename
        remote_copy = self.onedrive_config / self.config_copy

        # ConfigFile: Config / linux / dotfiles / zsh / .zshrc
        # ConfigCopy: Config / linux / dotfiles / copy / zsh / zsh.zshrc.copy

        local_mtime = self.config_path.stat().st_mtime
        remote_mtime = remote_conf.stat().st_mtime

        if local_mtime == remote_mtime:
            logger.warning("Remote and Local modify time is the same")
            return

        else:
            # TODO: implement file conflict algorithm
            # check for md5
            if self.config_path.is_dir():
                # self.config_path.iterdir()...
                pass  # save it for later
            else:
                ...

            if local_mtime > remote_mtime:
                logger.info(
                    f"Local {self.config_filename} file is newer. Syncing it to {self.onedrive_config}."
                )
                # make a copy of conf file in remote
                safe_copy(remote_conf, remote_copy)
                # replace remote conf with local conf
                safe_copy(self.config_path, remote_conf)
            elif local_mtime < remote_mtime:
                logger.info(
                    f"Remote {self.config_filename} file is newer. Syncing it to {self.config_path}"
                )
                # make a copy of conf file in local
                safe_copy(self.config_path, self.local_copy_path)
                # replace local conf with remote conf
                safe_copy(remote_conf, self.config_path)

