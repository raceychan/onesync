import asyncio
from asyncio import streams
from asyncio.events import get_event_loop, get_running_loop, AbstractEventLoop
from asyncio.unix_events import _UnixSelectorEventLoop
from asyncio.subprocess import Process, SubprocessStreamProtocol
from asyncio.protocols import BaseProtocol
from asyncio import SubprocessTransport
from typing import Unpack

from subprocess import CompletedProcess, PIPE
from pathlib import Path

from onesync.logs import logger
from onesync.interface import PopenPosixTypedDict


EXECUTABLE = "/usr/bin/zsh"
DEFAULT_STREAM_LIMIT: int = asyncio.streams._DEFAULT_LIMIT  # type: ignore

# sync version
# reff: https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
# You can direct the subprocess output to the streams directly. Simplified example:
# subprocess.run(['ls'], stderr=sys.stderr, stdout=sys.stdout)

# def sync_shell(cmd):
#     import subprocess
#
#     process = subprocess.Popen(
#         cmd,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         shell=True,
#         executable=EXECUTABLE,
#         encoding="utf-8",
#         errors="replace",
#     )
#
#     while (line := process.stdout.readline()) != "" or process.poll() is None:
#         if line:
#             print(line.strip(), flush=True)
#


# TODO: auto split multiple lines into multiple shells
def smart_cmd(cmd):
    return cmd


def get_unix_running_loop() -> _UnixSelectorEventLoop:
    loop = get_running_loop()
    return loop  # type: ignore


class StreamProcess(Process):
    _transport: SubprocessTransport
    _protocol: asyncio.subprocess.SubprocessStreamProtocol
    _loop: AbstractEventLoop

    def __init__(
        self,
        transport: SubprocessTransport,
        protocol: asyncio.subprocess.SubprocessStreamProtocol,
        loop: AbstractEventLoop,
    ):
        super().__init__(transport, protocol, loop)

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

    @classmethod
    async def construct(
        cls,
        stream_limit: int = DEFAULT_STREAM_LIMIT,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        universal_newlines=False,
        shell=True,
        bufsize=0,
        encoding=None,
        errors=None,
        text=None,
        **popendict: Unpack[PopenPosixTypedDict],
    ):
        loop = get_event_loop()

        protocol_factory = lambda: SubprocessStreamProtocol(
            limit=stream_limit, loop=loop
        )

        # NOTE: cmd gets excuted in this line
        transport, protocol = await loop.subprocess_shell(
            protocol_factory,
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            shell=shell,
            executable=executable,
            **popendict,
        )

        proc = cls(transport=transport, protocol=protocol, loop=loop)
        return proc


def shell_maker(
    stdin=PIPE,
    stdout=PIPE,
    stderr=PIPE,
    shell: bool = True,
    executable=EXECUTABLE,
    *,
    timeout=None,
    **kwargs: Unpack[PopenPosixTypedDict],
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
    # TODO: shell maker seem to be too complicated

    # quick fixcc

    executable = EXECUTABLE if Path("/usr/bin/zsh").exists() else None
    kwargs["executable"] = executable

    local_shell = shell_maker(**kwargs)
    proc = await local_shell(cmd)

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


class Shell:
    executeable: Path = ...

    def run(self, cmd):
        ...

    @classmethod
    async def construct(cls):
        ...


class Zshell(Shell):
    executable: Path = Path("/usr/bin/zsh")
    stream_limit: int = DEFAULT_STREAM_LIMIT

    def __init__(self, loop, process: StreamProcess):
        self.loop = loop
        self.process = process

    @classmethod
    async def construct(cls):
        return proc
