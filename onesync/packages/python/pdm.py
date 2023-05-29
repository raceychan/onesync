from base import shell

URL: str = "https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py"


def install():
    shell(f"curl -sSL {URL} | python3 -")
    shell("export PATH=/home/race/.local/bin:$PATH")
