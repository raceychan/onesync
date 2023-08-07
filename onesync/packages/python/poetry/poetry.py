from onesync.base import shell

# deprecated, use install.sh instead

SCRIPT_URL = "https://install.python-poetry.org"
POETRY_PATH = "~/.local/share/pypoetry"


async def _download_install_script():
    if True:  # if poetry is not already installed
        await shell(f"curl -sSL {SCRIPT_URL} | POETRY_HOME={POETRY_PATH} python3 -")


async def _export_path():
    await shell("export PATH=$HOME/.local/share/pypoetry/bin:$PATH")


async def _enable_autocomplt():
    await shell("poetry completions zsh > ~/.zfunc/_poetry")
    # adding these to .zshrc
    # fpath+=~/.zfunc
    # autoload -Uz compinit && compinit


async def install():
    await _download_install_script()
    await _export_path()
    await _enable_autocomplt()
