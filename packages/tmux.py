import shutil
from base import cmd
from pathlib import Path
from shutil import copy


config_path = Path("~/.tmux.conf")
alter_path = Path("~/.config/tmux/tmux.conf")


base_conf = """
set -g default-terminal "xterm-256color"
set-option -ga terminal-overrides ",xterm-256color:Tc"
"""


def _set_up_config():
    """
    set up conf file for tmux
    so that vim looks the same inside & outside of tmux

    test if there is  a symlink between config_path and alter_path  
    create one if not 
    """
    if alter_path.exists() and config_path.exists():
        return
    elif alter_path.exists():
        cmd(f"mv {alter_path} {config_path}")
    else:
        cmd(f"touch {config_path}")
        _set_up_config()



def install():

    cmd("")
