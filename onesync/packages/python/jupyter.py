import asyncio
from pathlib import Path
from onesync.base import shell, Package

LSP = {
    "pyright": "npm install --save-dev pyright",
    "sql": "npm install --save-dev sql-language-server",
    "markdown": "npm install --save-dev unified-language-server",
}
"""
>>> jupyter --paths

config:
    /home/race/.jupyter
data:
    /home/race/.local/share/jupyter
runtime:
    /home/race/.local/share/jupyter/runtime
"""


class Jupyter(Package):
    ...
    # labextensions address
    config_paht = "{conda_env}/share/jupyter/labextensions"


async def _install_pkgs():
    packages = [
        "jupyter",
        "jupyterlab",
        "jupyterlab_code_formatter",
        # "black",
        # "isort",
        "nb_conda_kernels",
        "jupyterlab-lsp",
        "python-lsp-server",
    ]

    txt = f"conda install -c conda-forge {' '.join(pck for pck in packages)}"
    await shell(txt)


async def _install_lsp():
    tasks = {shell(LSP[lsp] for lsp in LSP)}
    await asyncio.gather(*tasks)


def config():
    nb_conf = """
    {
    "CondaKernelSpecManager": {
    "kernelspec_path": "--user"
    }
    }
    """
    jp_conf = Path.home() / ".jupyter" / "jupyter_config.json"
    jp_conf.write_text(nb_conf)


async def install():
    await _install_pkgs()
    await _install_lsp()
