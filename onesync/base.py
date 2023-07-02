import shutil
from pathlib import Path
from subprocess import PIPE, CalledProcessError, CompletedProcess, run
from typing import Type
from abc import ABC, abstractmethod
from functools import cached_property
from dataclasses import dataclass, field
from typing import ClassVar

from loguru import logger

# from tomli import loads as load_toml


from onesync.config import SettingBase
from onesync.dirhash import md5sum

# TODO: use onesync.toml to parse

ProjectRoot = Path.cwd()

StrPath = str | Path


def _sync_copy_log(filename: str, src: Path, dst: Path):
    msg = f" Syncing {filename} from {src} to {dst}"
    logger.info(msg)


def copy(
    src: Path,
    dst: Path,
    *,
    follow_symlinks: bool = True,
    symlinks: bool = False,
    ignore=None,
    copy_function=shutil.copy2,
    ignore_dangling_symlinks: bool = False,
    dirs_exist_ok: bool = False,
    copy_empty_file: bool = True,
) -> Path:
    _sync_copy_log(src.name, src, dst)
    if not src.exists():
        raise Exception(f"source file {src.name} does not exist")

    if not copy_empty_file and src.stat().st_size == 0:
        raise Exception("Empty file bakcup is not allowed")

    if not dst.parent.exists():
        dst.parent.mkdir(parents=True)

    # dst can be either a file or a dir, either way, the parent would be a dir.
    if src.is_dir():
        path = shutil.copytree(
            src,
            dst,
            symlinks=symlinks,
            ignore=ignore,
            copy_function=copy_function,
            ignore_dangling_symlinks=ignore_dangling_symlinks,
            dirs_exist_ok=dirs_exist_ok,
        )
    else:
        path = shutil.copy(src, dst, follow_symlinks=follow_symlinks)
    return path


def shell(
    *args, timeout=60, shell=True, check=True, text=True, bufsize=-1, **kwargs
) -> CompletedProcess:
    # NOTE: rewrite needed so that output shows out on screen simutaneously
    logger.info(f"executing command with arguments: {args}")
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
        logger.error(f"{ce}")
        return CompletedProcess(*args, returncode=ce.returncode, stdout="", stderr="")
    else:
        if isinstance(cp.stdout, str):
            logger.success(cp.stdout)
        else:
            cp.stdout = ""
        return cp


def get_sys_number() -> str | None:
    res = shell("lsb_release -a 2>/dev/null | grep 'Release:' | awk '{print $2}'")
    if res and res.stdout:
        sys_num = res.stdout.strip()
    else:
        sys_num = None
    return sys_num


# provides a convenient way to combine commands, aim to replace multiple shell(command) call
class Command(str):
    def __new__(cls, *args):
        return super().__new__(cls, *args)

    def __and__(self, other):
        return " && ".join((self, other))


# dataclass = dataclass(kw_only=True)


@dataclass(kw_only=True)
class Package(ABC):
    # TODO: Package and its sublcasses should not require instantiation
    version: str = "latest"
    registry: ClassVar[dict[str, Type["Package"]]] = dict()
    dependencies: list = field(default_factory=list)

    @classmethod
    def from_settings(cls: Type["Package"], settings: SettingBase):
        """
        factory method to create Package instance using settings
        """
        raise NotImplementedError

    @classmethod
    def from_yaml(cls: Type["Package"], yaml: Path):
        ...

    def __init_subclass__(cls) -> None:
        cls.registry[cls.__module__] = cls

    @cached_property
    def name(self):
        return self.__class__.__name__.lower()

    @cached_property
    def doc(self):
        return self.__class__.__doc__

    @abstractmethod
    def install(self):
        """
        customized installing method of the package
        """
        raise NotImplementedError

    # @classmethod
    # def register(cls, *args, **kwargs):
    #     """
    #     A decorator used to register a class as package.

    #     @Package.register
    #     class Tmux:
    #         ...
    #     """

    #     class PackageLike:
    #         def __init__(self, pkg_clz: Type[Any]):
    #             ...

    #     def package_cls(pkg_clz: Type[Any]):
    #         cls.registry[pkg_clz.__module__] = pkg_clz
    #         return pkg_clz

    #     if not kwargs and len(args) == 1:
    #         # case where no args and kwargs were inputed
    #         ...
    #     else:
    #         wrapper = package_cls

    #     return package_cls

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


@dataclass
class Configurable(Package):
    config_path: Path
    onedrive_config: Path

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
            copy(self.config_path, remote_conf)
        elif not self.config_path.exists():
            copy(remote_conf, self.config_path)
        else:
            if md5sum(self.config_path) == md5sum(remote_conf):
                logger.info(f"{self.config_filename} is at its newest version")
                return
            self.update_conf()

    def update_conf(self):
        # NOTE: feature: support autosync using watchdog to detech file changes

        remote_conf = self.onedrive_config / self.config_filename
        remote_copy = self.onedrive_config / self.config_copy

        # config_file: Config / linux / dotfiles / zsh / .zshrc
        # config_copy: Config / linux / dotfiles / copy / zsh / zsh.zshrc.bak

        local_mtime = self.config_path.stat().st_mtime
        remote_mtime = remote_conf.stat().st_mtime

        if local_mtime == remote_mtime:
            logger.warning("Remote and Local modify time is the same")
            return

        # TODO: rewrite diff function for update_file, update_dir

        else:
            # TODO: implement file conflict algorithm
            if self.config_path.is_dir():
                # NOTE: when config path is a dir, calculate filehash of each file in it,
                # update only those changed,
                # self.config_path.iterdir()...
                pass  # save it for later

            if local_mtime > remote_mtime:
                logger.info(
                    f"Local {self.config_filename} file is newer. Syncing it to {self.onedrive_config}."
                )

                # make a copy of conf file in remote
                copy(remote_conf, remote_copy)

                # replace remote conf with local conf
                copy(self.config_path, remote_conf)

            elif local_mtime < remote_mtime:
                logger.info(
                    f"Remote {self.config_filename} file is newer. Syncing it to {self.config_path}"
                )
                # make a copy of conf file in local
                copy(self.config_path, self.local_copy_path)

                # replace local conf with remote conf
                copy(remote_conf, self.config_path)
