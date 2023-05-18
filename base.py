import shutil
from pathlib import Path
from subprocess import PIPE, CalledProcessError, CompletedProcess, run
from typing import Final, Union, Type, Any
from loguru import logger

# from tomli import loads as load_toml
from abc import ABC, abstractmethod
from functools import cached_property
from config import SettingBase


NONE_SENTINEL: Final = object()
ProjectRoot = Path.cwd()


StrPath = str | Path


def safe_copy(src: Path, dst: Path, *, follow_symlinks: bool = True) -> Path:
    if not src.exists():
        raise Exception(f"source file {src.name} does not exist")

    if src.stat().st_size == 0:
        raise Exception("Empty file bakcup is not allowed")

    if not dst.parent.exists():
        dst.parent.mkdir(parents=True)

    return shutil.copy(src, dst, follow_symlinks=follow_symlinks)


def cmd(
    *args, timeout=60, shell=True, check=True, text=True, bufsize=-1, **kwargs
) -> CompletedProcess | None:
    # NOTE: rewrite needed so that output shows out on screen simutaneously
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
        logger.error(ce.stderr)
        logger.info(f"Failed to execute {args}")
    else:
        if isinstance(cp.stdout, str):
            logger.success(cp.stdout)
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


def _sync_copy_log(filename: str, missed: Path, found: Path):
    msg = f"No {filename} file found in {missed}. Syncing {filename} from {missed} to {found}"
    logger.info(msg)


class Package(ABC):
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

    def __init__(self, *, config_file: Path, onedrive_config: Path):
        super().__init__()
        self.config_file = config_file
        self.onedrive_config = onedrive_config

    @classmethod
    def from_settings(cls: Type[Package], settings: SettingBase) -> "Configurable":
        return super().from_settings(settings)

    @cached_property
    def config_filename(self):
        if not self.config_file:
            raise Exception("config_file not set")
        return self.config_file.name

    @cached_property
    def config_copy(self) -> str:
        """
        Return filename is in the format ``"package.config_filename.copy"``

        Examples
        --------

        >>> package = zsh
        >>> config_filname = .zshrc
        >>> config_copy
        ... zsh.zshrc.copy
        """
        if self.config_file.name.startswith("."):
            file_name = f"{self.name}{self.config_file.name}.copy"
        else:
            file_name = f"{self.name}.{self.config_file.name}.copy"
        return file_name

    @cached_property
    def local_copy_path(self) -> Path:
        copy_path = Path.home() / ".config" / "onesync" / "dotfiles"
        local_copy = copy_path / self.config_copy
        return local_copy

    def sync_conf(self):
        """
        generated by GPT, modifications needed for a more generalized version.

        reff: https://techcommunity.microsoft.com/t5/ask-the-directory-services-team/understanding-dfsr-conflict-algorithms-and-doing-something-about/ba-p/397346
        File conflict algorithm
        """

        remote_conf = self.onedrive_config / self.config_filename

        if not self.config_file.exists() and not remote_conf.exists():
            raise FileNotFoundError(
                f"No {self.config_filename} file found in both {self.config_file} and {self.onedrive_config}."
            )
        elif not remote_conf.exists():
            _sync_copy_log(self.config_filename, self.onedrive_config, self.config_file)
            shutil.copy(self.config_file, remote_conf)
        elif not self.config_file.exists():
            _sync_copy_log(self.config_filename, self.config_file, self.onedrive_config)
            shutil.copy(remote_conf, self.config_file)
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

        local_mtime = self.config_file.stat().st_mtime
        remote_mtime = remote_conf.stat().st_mtime

        if local_mtime > remote_mtime:
            logger.info(
                f"Local {self.config_filename} file is newer. Syncing it to {self.onedrive_config}."
            )
            # make a copy of conf file in remote
            safe_copy(remote_conf, remote_copy)
            # replace remote conf with local conf
            safe_copy(self.config_file, remote_conf)
        elif local_mtime < remote_mtime:
            logger.info(
                f"Remote {self.config_filename} file is newer. Syncing it to {self.config_file}"
            )
            # make a copy of conf file in local
            safe_copy(self.config_file, self.local_copy_path)
            # replace local conf with remote conf
            safe_copy(remote_conf, self.config_file)
        else:
            # TODO: implement file conflict algorithm
            raise Exception("Remote and Local modify time is the same")
