# from base import Package

# class Jupyter(Package):
#     ...

def install():
    packages = [
    "jupyter", 
    "jupyterlab", 
    "jupyterlab_code_formatter", 
    "black" , 
    "isort", 
    "nb_conda_kernels", 
    "jupyterlab-lsp", 
    "python-lsp-server", 
    ]

    txt = f"conda install -c conda-forge {' '.join(pck for pck in packages)}"
    print(txt)
