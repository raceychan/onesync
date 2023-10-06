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

step1 ="""
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --d
"""

step2="""
NODE_MAJOR=20
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
"""

step3="""
sudo apt-get update
sudo apt-get install nodejs -y
"""
