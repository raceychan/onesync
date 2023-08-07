from onesync.base import shell


async def _add_repo():
    await shell("sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test")


async def install():
    await _add_repo()
    await shell("sudo apt install -y gcc-11")
