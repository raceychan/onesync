import os
from base import cmd, Package
from pathlib import Path



class ZSH(Package):
    plugins_dir = Path.home() / ".zsh" / "zsh-plugins"

    # install conda and python environment
    def install_p10k(self):
        path = self.plugins_dir / 'powerlevel10k'
        if not path.exists():
            res = cmd(f"""
            git clone --depth=1 https://github.com/romkatv/powerlevel10k.git {path}
            """)

        '''
        echo 'source ~/zsh-plugins/powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc
        '''

    def install_plugins(self):
        self.plugins_dir.mkdir(exist_ok=True)
        self.install_p10k()



        # cmd("chsh -s $(which zsh)")





    def install(self):
        '''
        most popular zsh plugins
        https://safjan.com/top-popular-zsh-plugins-on-github-2023/
        '''

        zrc_file = Path.cwd()/ "dotfiles"/ "zsh" / "zshrc"
        if not zrc_file.exists():
            raise Exception(f"default zshrc not found, please create zrc at {zrc_file}")

        if res := cmd("which zsh"):
            loc = res.stdout.decode('utf-8')
            # print(f'zsh installed at {loc}')

        self.install_plugins()
        



# ZSH().build()