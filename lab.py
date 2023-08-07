class LinuxDistrio:
    ...

class Ubuntu(LinuxDistrio):
    package_tool: "APT"

class Shell:
    ...

class UnixShell(Shell):
    distrio: LinuxDistrio 

    def install(self, package):
        self.distrio.package_tool.install(pacakge)


# shell = make_shell() # UnixShell(Ubuntu)
# 
# async with shell.stream() as sh:
#     await sh.cmd("ls")
#     await sh.cmd("mkdir sth")


# class PackgeTool:

    # def install():
        # raise NotImplementedError

    # def update():
        # raise NotImplementedError

# class APT(PackgeTool):
    # shell: ...
    # def install(package, yes=True):
        # await self.shell("apt install -y ...")

    # apt = APT(shell)
    # apt.install("zsh==1.3.1")