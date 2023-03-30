from base import cmd
from packages.zsh.zsh import ZSH

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

def continue_after_fail():
    ans = input('Failed to install core packages, do you want to continue? (y/n):')
    return ans in ACCEPTED_YES


# apt_packages_optional=["gnupg", "htop", "jq", "pass", "pwgen", "rsync", "shellcheck", "unzip"]

def apt_install(*packages):
    base_cmd = "sudo apt-get update && sudo apt-get install -y"
    if len(packages) == 1 and isinstance(packages, list):
        pkgs = " ".join(packages[0])
    else:
        pkgs = " ".join(packages)
    print(f"Installing {pkgs}")
    exec_result = cmd(f"{base_cmd} {pkgs}")
    return exec_result

def install_pkgs(pkgs:list[str]):
    pkg_str = " ".join(pkgs)
    install_optional = input("Do you want to install the Following optional packages? (y/n):" +"\n" + pkg_str + "\n")
    if install_optional in ACCEPTED_YES or install_optional == '':
        try:
            apt_install(pkg_str)
        except Exception:
            print('Failed to install optional packages')
    else:
        print('Failed to install packages')


def customize_install():
    # init zsh and set it to default shell
    ZSH().install()
    # install conda and python environment
    ...

def main():
    #install_pkgs(apt_pkgs)
    #install_pkgs(apt_enhanced_pkgs)
    customize_install()
    print('build ends')
    # cmd("ls")

if __name__ == "__main__":
    main()

































