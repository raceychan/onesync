from base import shell, safe_copy, Configurable
from pathlib import Path


config_file = Path("~/.tmux.conf")
alter_path = Path("~/.config/tmux/tmux.conf")


base_conf = """
set -g default-terminal "xterm-256color"
set-option -ga terminal-overrides ",xterm-256color:Tc"
"""


class Tmux(Configurable):
    config_file = ...


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
