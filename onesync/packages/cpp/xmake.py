from onesync.base import shell

def install():
    URL = "https://xmake.io/shget.text"
    shell(f"curl -fsSL {URL} | bash")
    shell("source ~/.xmake/profile")

