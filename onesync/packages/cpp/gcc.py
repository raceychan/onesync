from onesync.base import shell

def _add_repo():
    shell("sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test")

def install():
    _add_repo()
    shell("sudo apt install -y gcc-11")

