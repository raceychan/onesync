from pathlib import Path

from onesync.base import shell, copy, Configurable

config_file = Path("~/.tmux.conf")
alter_path = Path("~/.config/tmux/tmux.conf")


base_conf = """
set -g default-terminal "xterm-256color"
set-option -ga terminal-overrides ",xterm-256color:Tc"
"""
def default_tmux_conf():
    oh_my_tmux = "~/.config/tmux/oh_my_tmux"

    f"git clone https://github.com/gpakosz/.tmux.git {oh_my_tmux}"
    f'ln -s {oh_my_tmux} "~/.config/tmux/tmux.conf"'
    f"cp {oh_my_tmux}/.tmux.conf.local" "~/.config/tmux/tmux.conf.local"

def install_termnator():
    project_addr = "tmuxinator/tmuxinator/master/completion/tmuxinator.zsh" 
    local_addr = "/ush/local/shure/zsh/site-functions/_tmuxinator"
    cmd = f"wget https://raw.githubusercontent.com/{project_addr} -O {local_addr}"
    shell(cmd)

class Tmux(Configurable):
    config_file  = Path("~/.config/tmux/tmux.conf")

    def sync_conf(self):
        ...


def _set_up_config():
    """
    set up conf file for tmux
    so that vim looks the same inside & outside of tmux

    test if there is  a symlink between config_path and alter_path
    create one if not
    """
    if alter_path.exists() and config_file.exists():
        return
    elif alter_path.exists():
        shell(f"mv {alter_path} {config_file}")
    else:
        shell(f"touch {config_file}")
        _set_up_config()


def install():
    shell("")
