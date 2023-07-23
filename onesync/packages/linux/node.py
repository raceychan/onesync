from onesync.base import shell
from onesync.gitools import git_clone
from onesync.installer import apt_install


def _install_deps():
    deps ="dirmngr apt-transport-https lsb-release ca-certificates".split()
    apt_install(*deps)


def install():
    _install_deps()
    shell("curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash -")
    shell("sudo apt install -y nodejs")
