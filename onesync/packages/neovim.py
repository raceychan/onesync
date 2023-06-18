from base import git_clone, shell, Configurable
from pathlib import Path

# NOTE: since this is a configurable package, we should make this a Configurable class


def _download_latest_nvim():
    shell("sudo add-apt-repository -y ppa:neovim-ppa/stable")
    shell("sudo apt-get update && sudo apt-get install -y neovim")


class NeoVim(Configurable):
    pass


class NvChad(NeoVim):
    @classmethod
    def install(cls):
        git_clone("https://github.com/NvChad/NvChad", "~/.config/nvim", depth=1)


class LazyVim(NeoVim):
    @classmethod
    def install(cls):
        cls._backup_config()
        shell("git clone https://github.com/LazyVim/starter ~/.config/nvim")
        shell("rm -rf ~/.config/nvim/.git")

    @classmethod
    def _backup_config(cls):
        cmds = [
            # required
            "mv ~/.config/nvim ~/.config/nvim.bak",
            # optional but recommended
            "mv ~/.local/share/nvim ~/.local/share/nvim.bak",
            "mv ~/.local/state/nvim ~/.local/state/nvim.bak",
            "mv ~/.cache/nvim ~/.cache/nvim.bak",
        ]
        for cmd in cmds:
            shell(cmd)


def install():
    # _download_latest_nvim()
    LazyVim.install()


"""vim
let mapleader=',' " change the <leader> key to be comma

map <F1> <Esc> " avoid opening help on F1, let it be escape instead
imap <F1> <Esc>
nnoremap <CR> :noh<CR><CR> " hit enter to clear search highlighting
imap <expr><silent><C-h> pumvisible() ? deoplete#close_popup() .
      \ "\<Plug>(neosnippet_jump_or_expand)" : "\<CR>"
"""

import re
from typing import Tuple

vim_lua_mapping: dict = {
    "set": "vim.opt.",
    "let g:": "vim.g",  # note could be vim.g.sth or vim.g[sth]
    "let ": "vim.g",
}


class MappingNotFound(Exception):
    ...


class MatchNotFound(Exception):
    ...


def extract_mapping_info(
    mapping_string: str,
) -> Tuple[str, bool, str, str]:
    pattern = r"([inv])?(nore)?map\s+([\S]+)\s+([\S]+)"
    match = re.match(pattern, mapping_string)
    if not match:
        raise MatchNotFound

    mode = match.group(1)
    is_recursive = not bool(match.group(2))
    map_from = match.group(3)
    map_to = match.group(4)
    return mode, is_recursive, map_from, map_to


def convert_kmp(kmp: str):
    """
    convert keymap from vim style to lua stype

    from:
    vnoremap ga ^
    to:
    vim.api.nvim_set_keymap('v', 'ga', '^', {noremap = true})
    """

    try:
        mode, is_recursive, map_from, map_to = extract_mapping_info(kmp)
    except MappingNotFound:
        pass
    else:
        str = f"vim.api.nvim_set_keymap('{mode}', '{map_from}', '{map_to}', {{noremap}} = {'true' if is_recursive else 'false'})"
        return str


def vimrc_to_lua(vimrc: Path, to: Path):
    # TODO: use AST parse tree to analyze?
    with vimrc.open() as f:
        for line in f.readlines():
            if not line:
                continue
            match line.split('"'):
                case ["", comment]:
                    print("comment", comment)
                case [command]:
                    if not command:
                        raise Exception("empty command")

                    match command.split(" "):
                        case ["set", content]:
                            print("set", content)
                        case _:
                            print("undefined", command)
                case _:
                    print(f"Command '{line}' not understood")
