from base import cmd, git_clone


def _install_deps():
    cmd(
        "sudo apt -y install curl dirmngr apt-transport-https lsb-release ca-certificates"
    )


def install():
    _install_deps()
    cmd("curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash -")
    cmd("sudo apt install -y nodejs")
