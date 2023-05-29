from base import shell, get_sys_number

# step 1: add the opensuse build service repository release key
# Add the OpenSuSE Build Service repository release key using the following command:

# wget -qo - https://download.opensuse.org/repositories/home:/npreining:/debian-ubuntu-onedrive/xubuntu_22.04/release.key | gpg --dearmor | sudo tee /usr/share/keyrings/obs-onedrive.gpg > /dev/null

# step 2: add the opensuse build service repository

# echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/obs-onedrive.gpg] https://download.opensuse.org/repositories/home:/npreining:/debian-ubuntu-onedrive/xubuntu_22.04/ ./" | sudo tee /etc/apt/sources.list.d/onedrive.list

# step 3: update your apt package cache
# run: sudo apt-get update

# step 4: install 'onedrive'
# run: sudo apt install --no-install-recommends --no-install-suggests onedrive


def _remove_old_onedrive():
    shell(
        "sudo apt remove onedrive && sudo add-apt-repository --remove ppa:yann1ck/onedrive >> /dev/null 2>&1"
    )


def _download_and_add_release_key():
    # Download the 'Release.key' file:
    sys_num = get_sys_number()
    url = f"https://download.opensuse.org/repositories/home:/npreining:/debian-ubuntu-onedrive/xUbuntu_{sys_num}/Release.key"
    shell(
        f"wget -qO - {url} | gpg --dearmor | sudo tee /usr/share/keyrings/obs-onedrive.gpg > /dev/null"
    )


def _add_opensuse_repo():
    shell(
        'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/obs-onedrive.gpg] https://download.opensuse.org/repositories/home:/npreining:/debian-ubuntu-onedrive/xUbuntu_22.04/ ./" | sudo tee /etc/apt/sources.list.d/onedrive.list'
    )
    shell("sudo apt-get update")


def _install_onedrive():
    shell("sudo apt install --no-install-recommends --no-install-suggests onedrive")


def install():
    _remove_old_onedrive()
    _download_and_add_release_key()
    _add_opensuse_repo()
    _install_onedrive()
