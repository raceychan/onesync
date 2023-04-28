from base import cmd

# class Jupyter(Package):
#     ...
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


def _install_pkgs():
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
    cmd(txt)


def _install_lsp():
    for lsp in LSP:
        cmd(LSP[lsp])


def install():
    _install_pkgs()
    _install_lsp()
