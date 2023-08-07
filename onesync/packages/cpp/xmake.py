from onesync.base import shell


async def install():
    URL = "https://xmake.io/shget.text"
    await shell(f"curl -fsSL {URL} | bash")
    await shell("source ~/.xmake/profile")
