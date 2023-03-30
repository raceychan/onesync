import os
import shutil
from base import cmd, Package
from pathlib import Path
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__file__)


#TODO: move to base
def git_clone(target: str, local: str | Path, **kwargs):
    extra = ''.join('--{k}={v}' for k, v in kwargs.values()) if kwargs else ''

    logger.info(f'cloning {target} into {local}')


    git = f"git clone {extra}{' ' if extra else ''}{target} {local}"
    cmd(git)
    return local

class ZSH(Package):
    root_dir: Path =  Path.home() / ".zsh"
    plugins_dir: Path = root_dir/ "zsh-plugins"
    as_default: bool = True


    # install conda and python environment

    def install_p10k(self):
        path = self.plugins_dir / 'powerlevel10k'

        if not path.exists():
            res = cmd(f"""
            git clone --depth=1 https://github.com/romkatv/powerlevel10k.git {str(path)}
            """)

        # cmd(f'''echo 'source {path}/powerlevel10k.zsh-theme' >>~/.zshrc''')


    def install_zsh_nord(self):
        ...

    def install_autojump(self):
        path = self.plugins_dir / 'autojump'
        git_clone('git://github.com/wting/autojump.git', str(path))

        # cmd(f'git clone git://github.com/wting/autojump.git {str(path)}')
        # cmd('cd ~/zsh-plugins/autojump')
        # cmd('python install.py')

        install_py = path / 'install.py'

        cmd(f'python {str(install_py)}')

    def install_plugins(self):
        # TODO: rewrite this, accept a list of plugins
        logger.info(f'installing {self.name} plugins')
        self.plugins_dir.mkdir(exist_ok=True)
        # self.install_p10k()
        self.install_autojump()


    def install(self, **kwargs):
        '''
        most popular zsh plugins
        https://safjan.com/top-popular-zsh-plugins-on-github-2023/
        '''

        self.install_plugins()
        self.setup_zshrc()


        if self.as_default and not self.is_default_shell:
            sh_path = str(Path(__file__).parent / 'set_as_default.sh')
            logger.warning(f"{self.name} is not default shell, execute {sh_path} to change")

    def setup_zshrc(self):
        zrc_file = Path.cwd()/ "dotfiles"/ "zsh" / "zshrc"
        if not zrc_file.exists():
            raise Exception(f"default zshrc not found, please create zrc at {zrc_file}")

        target = Path.home() /'.zshrc'
        if target.exists():
            shutil.copyfile(zrc_file, target)


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


#### better way to deal with unpredictable shell script output given by chatgpt
# import asyncio
# import os
# from typing import TextIO
# 
# def create_shell_script(script_path: str) -> None:
#     with open(script_path, "w") as script_file:
#         script_file.write("#!/bin/bash\n")
#         script_file.write("echo 'Welcome to the unpredictable script!'\n")
#         script_file.write("echo 'Enter your name:'\n")
#         script_file.write("read name\n")
#         script_file.write("echo \"Hello, $name!\"")
# 
#     os.chmod(script_path, 0o755)
# 
# async def handle_script_output(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
#     while not reader.at_eof():
#         line = await reader.readline()
#         output = line.decode("utf-8").strip()
#         if output:
#             print(output)
#             if "Enter your name:" in output: # BUG: this still assumes output is predictable
#                 user_input = input()
#                 writer.write(f"{user_input}\n".encode("utf-8"))
#                 await writer.drain()
# 
# async def execute_shell_script_unpredictable_output(script_path: str) -> None:
#     process = await asyncio.create_subprocess_exec(
#         script_path,
#         stdin=asyncio.subprocess.PIPE,
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE,
#     )
#     
#     if not (process.stdin and process.stdout):
#         raise Exception("Error: stdout or stdin is None")
# 
#     await handle_script_output(process.stdout, process.stdin)
# 
#     if process.stderr:
#         stderr = await process.stderr.read()
#     else:
#         stderr = None
# 
#     return_code = await process.wait()
# 
#     if return_code != 0 or stderr:
#         print("An error occurred:")
#         if stderr:
#             print(stderr.decode("utf-8"))
# 
# if __name__ == "__main__":
#     script_path = "test_script.sh"
#     create_shell_script(script_path)
# 
#     asyncio.run(execute_shell_script_unpredictable_output(script_path))
# 