import asyncio

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    print(proc.stdin, proc.stdout,proc.stderr)

    print(f'executing {cmd}')
    stdout, stderr = await proc.communicate()
    print(stdout, stderr)

    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')

def test():
    import subprocess, sys
    p = subprocess.Popen('chsh -s $(which zsh)', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while p.poll() is None:
        sys.stdout.write(p.stdout.read(1).decode(sys.stdout.encoding))
        sys.stdout.flush()
    
