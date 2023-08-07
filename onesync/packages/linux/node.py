from onesync.base import shell
from onesync.gitools import git_clone
from onesync.installer import apt_install


async def _install_deps():
    deps = "dirmngr apt-transport-https lsb-release ca-certificates".split()
    await apt_install(*deps)


async def install():
    await _install_deps()
    await shell("curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash -")
    await shell("sudo apt install -y nodejs")
