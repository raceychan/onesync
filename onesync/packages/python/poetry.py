from onesync.base import shell


SCRIPT_URL = "https://install.python-poetry.org"
POETRY_PATH = "~/.local/share/pypoetry"


def _download_install_script():
    if ...:  # if poetry is not already installed
        shell(f"curl -sSL {SCRIPT_URL} | POETRY_HOME={POETRY_PATH} python3 -")


def _export_path():
    shell("export PATH=$HOME/.local/share/pypoetry/bin:$PATH")


def _enable_autocomplt():
    shell("poetry completions zsh > ~/.zfunc/_poetry")
    # adding these to .zshrc
    # fpath+=~/.zfunc
    # autoload -Uz compinit && compinit


def install():
    _download_install_script()
    _export_path()
    _enable_autocomplt()
