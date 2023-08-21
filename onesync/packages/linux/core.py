# from base import load_toml
from onesync.base import Package
from onesync.config import read_dependency
from onesync.installer import apt_install


def make_package(name):
    return type(name, (Package,), {})


# TODO: read from dependency.toml
apt_pkgs = read_dependency("sys.base")

apt_enhanced_pkgs = read_dependency("sys.enhanced")

apt_packages_optional = read_dependency("sys.optional")

# NOTE: some of these packages needs extra care
# e.g: exa can't be installed natively in Ubuntu 20


async def install():
    """
    # TODO: install all sub-packages of zsh within a same function. better abstraction needed

    #dependencies.toml
    [zsh.plugins]
    auto-suggestion=...

    for plugin in self.plugins:
        self.install_plugins(plugin)
    """
    pkgs = apt_pkgs + apt_enhanced_pkgs
    await apt_install(pkgs)
