from base import shell, git_clone


def _install_deps():
    shell(
        "sudo apt -y install curl dirmngr apt-transport-https lsb-release ca-certificates"
    )


def install():
    _install_deps()
    shell("curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash -")
    shell("sudo apt install -y nodejs")
