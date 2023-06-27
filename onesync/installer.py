from .base import shell
from .config import settings


def continue_after_fail():
    ans = input("Failed to install core packages, do you want to continue? (y/n):")
    return ans in settings.ACCEPTED_YES


# deprecated, rewrite needed
def apt_install(*packages):
    base_cmd = "sudo apt-get update && sudo apt-get install -y"
    if len(packages) == 1 and isinstance(packages[0], list):
        pkgs = " ".join(packages[0])
    else:
        pkgs = " ".join(packages)
    print(f"Installing {pkgs}")
    exec_result = shell(f"{base_cmd} {pkgs}")
    return exec_result


# deprecated, rewrite needed
def install_pkgs(pkgs: list[str]):
    pkg_str = " ".join(pkgs)
    install_optional = input(
        "Do you want to install the Following optional packages? (y/n):"
        + "\n"
        + pkg_str
        + "\n"
    )
    if install_optional in settings.ACCEPTED_YES or install_optional == "":
        try:
            apt_install(pkg_str)
        except Exception:
            print("Failed to install optional packages")
    else:
        print("Failed to install packages")
