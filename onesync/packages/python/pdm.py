# from onesync.base import shell

URL: str = "https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py"


async def install(shell):
    await shell("conda activate base")
    await shell("sudo apt install python3.10-venv")
    await shell(f"curl -sSL {URL} | python3 -")
    await shell("export PATH=/home/race/.local/bin:$PATH")
