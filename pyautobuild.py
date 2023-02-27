# import os
# import subprocess
from base import cmd
from zsh import ZSH

ACCEPTED_YES = ["y", "yes", "Y", "YES"]

apt_pkgs = [
    "zsh", 
    "curl", 
    "ncdu", 
    "git", 
    "iproute2", 
    "python3-pip",
    "ripgrep", 
    "tmux"
]

apt_enhanced_pkgs = [
    "httpie", 
    "exa", 
    "neovim", 
    "bat",
    "btop",
    "net-tools",
    "ncdu", 
    "fzf", 
    "ranger", 
    "tree"
]



# apt_packages_optional=["gnupg", "htop", "jq", "pass", "pwgen", "rsync", "shellcheck", "unzip"]

def apt_install(*packages):
    base_cmd = "sudo apt-get update && sudo apt-get install -y"
    if len(packages) == 1 and isinstance(packages, list):
        pkgs = " ".join(packages[0])
    else:
        pkgs = " ".join(packages)
    exec_result = cmd(f"{base_cmd} {pkgs}")
    return exec_result

def install_core_pkgs():
    pkg_list = " ".join(apt_pkgs) 
    opt_pkg_list = " ".join(apt_enhanced_pkgs)

    try:
        apt_install(pkg_list)
    except Exception:
        if input('Failed to install core packages, do you want to continue? (y/n):') not in ACCEPTED_YES:
            print('Exiting...')
            return

    if input("do you want to install the Following packages? (y/n):" +"\n" + opt_pkg_list + "\n") in ACCEPTED_YES:
        try:
            apt_install(opt_pkg_list)
        except Exception:
            print('Failed to install optional packages')

    # init zsh and set it to default shell
    ZSH().setup()

    # install conda and python environment

def customize_install():
    ...

def main():
    install_core_pkgs()
    customize_install()
    # cmd("ls")

if __name__ == "__main__":
    main()

































