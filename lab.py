class PackgeTool:
    def install(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


class APT(PackgeTool):
    shell: ...

    async def install(package, yes=True):
        await self.shell("apt install -y ...")


# apt = APT(shell)
# apt.install("zsh==1.3.1")
class LinuxDistrio:
    package_tool: "APT"


class Ubuntu(LinuxDistrio):
    package_tool: "APT"


class Shell:
    ...


class UnixShell(Shell):
    distrio: LinuxDistrio

    async def install(self, package):
        await self.distrio.package_tool.install(pacakge)


# shell = make_shell() # UnixShell(Ubuntu)
#
# async with shell.stream() as sh:
#     await sh.cmd("ls")
#     await sh.cmd("mkdir sth")
from loguru import logger


async def test_shell(cmd):
    logger.opt(depth=1).info("hello")


async def test_depth_1():
    await test_depth_2()


async def test_depth_2():
    await test_depth_3()


async def test_depth_3():
    await test_shell("apt install neovim")


async def install():
    await test_depth_1()


import asyncio

asyncio.run(install())
