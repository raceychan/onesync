import shutil
from base import cmd, Package, git_clone, NONE_SENTINEL, logger
from pathlib import Path





class ZSH(Package):

    def __init__(self, root_dir: Path | None = None, as_default: bool = True):
        super().__init__()
        self.root_dir = root_dir or Path.home() / ".zsh"
        self.as_default = as_default
        self._is_installed = False

    @property
    def is_installed(self) -> bool:
        return self._is_installed

    @property
    def plugins_dir(self) -> Path:
        return self.root_dir / "zsh-plugins"

    # install conda and python environment

    def install_p10k(self):
        path = self.plugins_dir / 'powerlevel10k'
        if not path.exists():
            git_clone('https://github.com/romkatv/powerlevel10k.git', path, depth=1)
            cmd(f'''echo 'source {path}/powerlevel10k.zsh-theme' >>~/.zshrc''')

    def install_zsh_nord(self):
        path = self.plugins_dir / 'zsh-dircolors-nord'
        if not path.exists():
            git_clone("https://github.com/coltondick/zsh-dircolors-nord.git", path, recursive=NONE_SENTINEL)
            cmd(f'source {path}/zsh-dircolors-nord.zsh')

    def install_zsh_autosuggestion(self):
        path = self.plugins_dir / 'zsh-autosuggestions'
        if not path.exists():
            git_clone("https://github.com/zsh-users/zsh-autosuggestions", path)
            cmd(f"source {str(path)}/zsh-autosuggestions.zsh")

    def install_synx_highlighting(self):
        path = self.plugins_dir / 'zsh-syntax-highlighting'
        if not path.exists():
            git_clone('https://github.com/zsh-users/zsh-syntax-highlighting.git', path)
            cmd(f'source {str(path)}/zsh-syntax-highlighting.zsh')

    def install_autojump(self):
        path = self.plugins_dir / 'autojump'
        if not path.exists():
            git_clone('git@github.com:wting/autojump.git', str(path))
            install_py = path / 'install.py'
            cmd(f'cd {str(path)} && python {str(install_py)}')

    def install_plugins(self):
        '''
        most popular zsh plugins
        https://safjan.com/top-popular-zsh-plugins-on-github-2023/
        '''

        # TODO: rewrite this, accept a list of plugins
        logger.info(f'installing {self.name} plugins')
        self.plugins_dir.mkdir(exist_ok=True)
        
        self.install_p10k()
        self.install_autojump()
        self.install_zsh_nord()
        self.install_zsh_autosuggestion()
        self.install_synx_highlighting()

    def setup_zshrc(self):
        zrc_file = Path.cwd()/ "dotfiles"/ "zsh" / "zshrc"
        if not zrc_file.exists():
            logger.warning(f"default zshrc not found, please create zrc at {zrc_file}")
            # raise Exception(f"default zshrc not found, please create zrc at {zrc_file}")

        target = Path.home() /'.zshrc'
        if target.exists():
            shutil.copyfile(zrc_file, target)

    def install(self, **kwargs):
        self.install_plugins()
        # self.setup_zshrc()

        if self.as_default and not self.is_default_shell:
            sh_path = Path(__file__).parent / 'set_as_default.sh'
            logger.warning(f"{self.name} is not default shell, execute {str(sh_path)} to change")
        
        self._is_installed = False


    @property
    def is_default_shell(self):
        res = cmd("ps -p $$ | awk 'FNR == 2 {print $4}'")
        return True # BUG, res.stdout returns sh\n
        # return (res and res.stdout == self.name)



#    def set_as_default(self):        
#        # problem here: subprocess can't show prompt
#        # in this case when type the cmd, it quires password
#        # but the subprocess module wouldnt print it out because it's blocking
#        sh_path = str(Path(__file__).parent / 'set_as_default.sh')
#        cmd(sh_path)

# ZSH().build()


