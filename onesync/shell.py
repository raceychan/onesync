import sys
import asyncio
from asyncio import streams
from asyncio.events import get_event_loop, get_running_loop, AbstractEventLoop
from asyncio.unix_events import _UnixSelectorEventLoop
from asyncio.subprocess import Process, SubprocessStreamProtocol
from asyncio.protocols import BaseProtocol
from asyncio import SubprocessTransport

from subprocess import CompletedProcess, PIPE, run as sync_run

from onesync.logs import logger

EXECUTABLE = "/usr/bin/zsh"
DEFAULT_STREAM_LIMIT: int = asyncio.streams._DEFAULT_LIMIT  # type: ignore

# there could be a sync version
# reff: https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
# You can direct the subprocess output to the streams directly. Simplified example:
# subprocess.run(['ls'], stderr=sys.stderr, stdout=sys.stdout)


# TODO: auto split multiple lines into multiple shells
def smart_cmd(cmd):
    return cmd


def get_unix_running_loop() -> _UnixSelectorEventLoop:
    loop = get_running_loop()
    return loop  # type: ignore


class StreamProcess(Process):
    _transport: SubprocessTransport
    _protocol: BaseProtocol
    _loop: AbstractEventLoop

    stdout: streams.StreamReader
    stderr: streams.StreamReader
    stdin: streams.StreamReader
    pid: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def display_info(self):
        # TODO: logger should not display shell:display_info:46
        # instead, display the caller's function

        async for line in self.stdout:
            logger.info(line.decode())

    async def display_error(self):
        async for line in self.stderr:
            logger.error(line.decode())

    async def display_output(self):
        coros = list()
        if self.stdout is not None:
            coros.append(self.display_info())

        if self.stderr is not None:
            coros.append(self.display_error())

        await asyncio.gather(*coros)


def shell_maker(
    stdin=PIPE,
    stdout=PIPE,
    stderr=PIPE,
    shell: bool = True,
    executable=EXECUTABLE,
    *,
    timeout=None,
    **kwargs,
):
    limit = DEFAULT_STREAM_LIMIT

    async def shell_maker(cmd, *, timeout=None):
        loop = get_event_loop()
        protocol_factory = lambda: SubprocessStreamProtocol(limit=limit, loop=loop)

        # NOTE: cmd gets excuted in this line
        transport, protocol = await loop.subprocess_shell(
            protocol_factory,
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            shell=shell,
            executable=executable,
            **kwargs,
        )

        proc = StreamProcess(transport=transport, protocol=protocol, loop=loop)
        return proc

    return shell_maker


async def shell(cmd, **kwargs):
    shell = shell_maker(**kwargs)
    proc = await shell(cmd)

    # 0 means success else means failure, would return None before proc.wait
    if proc.returncode:
        print("return code: ", proc.returncode)

    # NOTE: this returns after process finishes execution
    try:
        await proc.display_output()
        await proc.wait()
    except Exception:
        await proc.wait()
    except KeyboardInterrupt:
        proc.kill()
        raise

    # temp solution for proc.returncode could be None
    return_code = proc.returncode or 1
    return CompletedProcess(cmd, returncode=return_code, stdout="", stderr="")


def sync_shell(cmd):
    import subprocess

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        executable=EXECUTABLE,
        encoding="utf-8",
        errors="replace",
    )

    while (line := process.stdout.readline()) != "" or process.poll() is None:
        if line:
            print(line.strip(), flush=True)


async def test_long_cmd():
    cmd = """for (( i = 0; i < 3; i++ )); do echo "Current time: $(date +"%T")"; sleep 1; done"""
    sync_shell(cmd)
    # sync_run(cmd, stdout=sys.stdout, shell=True, executable=EXECUTABLE)
    # await shell(cmd)


async def test_err_cmd():
    cmd = "cat non_existent_file.txt"
    await shell(cmd)


async def test_async_group():
    await asyncio.gather(test_long_cmd(), test_err_cmd())


async def main():
    await test_long_cmd()


if __name__ == "__main__":
    asyncio.run(main())
