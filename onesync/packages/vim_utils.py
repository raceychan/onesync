import re
from typing import Tuple
from pathlib import Path

vim_lua_mapping: dict = {
    "set": "vim.opt.",
    "let g:": "vim.g",  # note could be vim.g.sth or vim.g[sth]
    "let ": "vim.g",
}


KEYMAP_RE = re.compile(r"([inv])?(nore)?map\s+([\S]+)\s+([\S]+)")


class MappingNotFound(Exception):
    ...


class MatchNotFound(Exception):
    ...


def _extract_mapping_info(
    mapping_string: str,
) -> Tuple[str, bool, str, str]:
    match = KEYMAP_RE.match(mapping_string)
    if not match:
        raise MatchNotFound

    mode = match.group(1) or ""
    noremap = not bool(match.group(2))
    map_from = match.group(3) or ""
    map_to = match.group(4) or ""
    return mode, noremap, map_from, map_to


def to_lua_table(_filterd_bool={True, False, None}, **kwargs) -> str:
    def filter_bool(v):
        if v in _filterd_bool:
            v = str(v).lower()
        return v

    holder = "".join([f" {k} = {filter_bool(v)} , " for k, v in kwargs.items()])
    lua_table = f"""{"{"}{holder.removesuffix(', ')}{"}"}"""
    return lua_table


def lua_kmp(kmp: str) -> str:
    """
    convert keymap from vim style to lua stype

    from:
    vnoremap ga ^
    to:
    vim.api.nvim_set_keymap('v', 'ga', '^', {noremap = true})
    """

    mode, noremap, map_from, map_to = _extract_mapping_info(kmp)
    kw = to_lua_table(noremap=noremap)
    lua = f'vim.api.nvim_set_keymap("{mode}", "{map_from}", "{map_to}", {kw})'
    return lua


def lua_set(set_cmd: str):
    pass


def lua_let(let_cmd: str):
    pass


def vimrc_to_lua(vimrc: Path, to: Path):
    """
    prefixes = ['foo', 'bar', 'baz']
    rx = re.compile(''.join(['^(?:', '|'.join(prefixes), ')']))
    for line in input:
        cmd_type = rx.match(line)
        if cmd_type:
            matched = match.group(0)
        match cmd_type:
            ...
    """
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
