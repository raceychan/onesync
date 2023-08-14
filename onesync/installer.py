from onesync.base import shell
from onesync.config import settings


def continue_after_fail():
    ans = input("Failed to install core packages, do you want to continue? (y/n):")
    return ans in settings.ACCEPTED_YES


# rewrite needed
async def apt_install(*packages):
    base_cmd = "sudo apt-get update && sudo apt-get install -y"
    if len(packages) == 1 and isinstance(packages[0], list):
        pkgs = " ".join(packages[0])
    else:
        pkgs = " ".join(packages)
    print(f"Installing {pkgs}")
    exec_result = await shell(f"{base_cmd} {pkgs}")
    return exec_result


# deprecated, rewrite needed
async def install_pkgs(pkgs: list[str]):
    pkg_str = " ".join(pkgs)
    install_optional = input(
        "Do you want to install the Following optional packages? (y/n):"
        + "\n"
        + pkg_str
        + "\n"
    )
    if install_optional in settings.ACCEPTED_YES or install_optional == "":
        try:
            await apt_install(pkg_str)
        except Exception:
            print("Failed to install optional packages")
    else:
        print("Failed to install packages")


class PackageTool:
    def install(self, package_name):
        pass

    def remove(self, package_name):
        pass

    # Add other package tool methods here




    # Implement other APT-specific methods here


class Platform:
    def __init__(self, package_tool):
        self.package_tool = package_tool

    def install_package(self, package_name):
        self.package_tool.install(package_name)

    def remove_package(self, package_name):
        self.package_tool.remove(package_name)

    # Add other platform methods here


class Unix(Platform):
    def __init__(self, package_tool: PackageTool):
        super().__init__(package_tool)

    # Implement Unix-specific methods here


class Linux(Unix):
    def __init__(self, package_tool: PackageTool):
        super().__init__(package_tool)

    # Implement Linux-specific methods here


class Ubuntu(Linux):
    package_tool: "APT"

    def __init__(self, package_tool: "APT"):
        super().__init__(package_tool)


class APT(PackageTool):
    prefix: str = "apt-get"

    def __init__(self, root: bool=True):
        self.root = root

    def run_as_root(self, cmd: str):
        return f"sudo {cmd}" if self.root else cmd

    async def update(self):
        return self.run_as_root("apt-get update")

    async def install(self, package):
        return self.run_as_root(f"{self.prefix} install -y {package}")

    def remove(self, package):
        return self.run_as_root(f"{self.prefix} remove {package}")