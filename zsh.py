import os
from base import cmd, Package
from pathlib import Path



class ZSH(Package):
    ...

    # install conda and python environment

    def setup(self):
        '''
        most popular zsh plugins
        https://safjan.com/top-popular-zsh-plugins-on-github-2023/
        '''
        zrc = Path.cwd()/ "dotfiles"/ "zsh" / "zshrc"
        if not zrc.exists():
            raise Exception(f"zshrc not found, please create zrc at {zrc}")

        ...

    def install_plugins(self):

        plugin_dir = Path.home() / ".zsh" / "zsh-plugins"
        plugin_dir.mkdir()
        # cmd("chsh -s $(which zsh)")

    def install(self):
        self.setup()

# ZSH().build()