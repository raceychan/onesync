from onesync.base import shell


async def install():
    await shell("pip install pipx")
