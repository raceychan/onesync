from onesync.base import shell, get_sys_number, Package, CommandGroup
from pathlib import Path

"""
reff:
https://github.com/abraunegg/onedrive/blob/master/docs/ubuntu-package-install.md


step 1: add the opensuse build service repository release key
Add the OpenSuSE Build Service repository release key using the following command:

wget -qo - https://download.opensuse.org/repositories/home:/npreining:/debian-ubuntu-onedrive/xubuntu_22.04/release.key | gpg --dearmor | sudo tee /usr/share/keyrings/obs-onedrive.gpg > /dev/null

step 2: add the opensuse build service repository

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/obs-onedrive.gpg] https://download.opensuse.org/repositories/home:/npreining:/debian-ubuntu-onedrive/xubuntu_22.04/ ./" | sudo tee /etc/apt/sources.list.d/onedrive.list

step 3: update your apt package cache
run: sudo apt-get update

step 4: install 'onedrive'
run: sudo apt install --no-install-recommends --no-install-suggests onedrive
"""


class OneDrive(Package):

    async def _remove_old_onedrive(self):
        await shell(
            "sudo apt remove onedrive && sudo add-apt-repository --remove ppa:yann1ck/onedrive >> /dev/null 2>&1"
        )
        self.remove_symlink()

    async def purge_system(self):
        await shell(CommandGroup(
            """
            rm -rf /var/lib/dpkg/lock-frontend
            rm -rf /var/lib/dpkg/lock
            apt-get update
            apt-get upgrade -y
            apt-get dist-upgrade -y
            apt-get autoremove -y
            apt-get autoclean -y
            """
        ))


    async def _download_and_add_release_key(self):
        # Download the 'Release.key' file:
        sys_num = get_sys_number()
        url = f"https://download.opensuse.org/repositories/home:/npreining:/debian-ubuntu-onedrive/xUbuntu_{sys_num}/Release.key"
        await shell(
            f"wget -qO - {url} | gpg --dearmor | sudo tee /usr/share/keyrings/obs-onedrive.gpg > /dev/null"
        )

    def create_symlink(self):
        # Created symlink /etc/systemd/user/default.target.wants/onedrive.service → /usr/lib/systemd/user/onedrive.service.
        systemd_entry =  Path("/etc/systemd/user/default.target.wants/onedrive.service")
        systemd_entry.symlink_to(
            "/usr/lib/systemd/user/onedrive.service"
        )

    def remove_symlink(self):
        systemd_entry =  Path("/etc/systemd/user/default.target.wants/onedrive.service")
        if systemd_entry.is_symlink():
            systemd_entry.unlink()

    async def _add_opensuse_repo(self):
        await shell(
            'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/obs-onedrive.gpg] https://download.opensuse.org/repositories/home:/npreining:/debian-ubuntu-onedrive/xUbuntu_22.04/ ./" | sudo tee /etc/apt/sources.list.d/onedrive.list'
        )
        await shell("sudo apt-get update")


    async def _install_onedrive(self):
        await shell("sudo apt install --no-install-recommends --no-install-suggests onedrive")


    async def install(self):
        await self._remove_old_onedrive()
        await self._download_and_add_release_key()
        await self._add_opensuse_repo()
        await self._install_onedrive()
