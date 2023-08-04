import asyncio
from asyncio import streams
from asyncio.events import get_event_loop, get_running_loop, AbstractEventLoop
from asyncio.unix_events import _UnixSelectorEventLoop
from asyncio.subprocess import Process, SubprocessStreamProtocol
from asyncio.protocols import BaseProtocol
from asyncio import SubprocessTransport

from subprocess import CompletedProcess, CalledProcessError, PIPE, run as sync_run

from loguru import logger

EXECUTABLE = "/usr/bin/zsh"
DEFAULT_STREAM_LIMIT: int = asyncio.streams._DEFAULT_LIMIT  # type: ignore

# there could be a sync version
# reff: https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess


class TypedProcess(Process):
    _transport: SubprocessTransport
    _protocol: BaseProtocol
    _loop: AbstractEventLoop

    stdout: streams.StreamReader
    stderr: streams.StreamReader
    stdin: streams.StreamReader
    pid: int

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)


def smart_cmd(cmd):
    # TODO: auto split multiple lines into multiple shells
    return cmd


def get_unix_running_loop() -> _UnixSelectorEventLoop:
    loop = get_running_loop()
    return loop  # type: ignore


async def get_shell(cmd, **kwargs):
    limit = DEFAULT_STREAM_LIMIT
    loop = get_event_loop()
    protocol_factory = lambda: SubprocessStreamProtocol(limit=limit, loop=loop)

    # NOTE: cmd gets excuted in this line
    transport, protocol = await loop.subprocess_shell(
        protocol_factory,
        cmd,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
        executable=EXECUTABLE,
        **kwargs,
    )

    proc = Process(transport=transport, protocol=protocol, loop=loop)
    return proc


async def shell(cmd, **kwargs):
    proc = await get_shell(cmd, **kwargs)

    async for l in proc.stdout:
        logger.info(l.decode())

    async for e in proc.stderr:
        logger.info(e.decode())

    await proc.wait()

    # 0 means success else means failure, would return None before proc.wait
    if proc.returncode:
        print(proc.returncode)

    # NOTE: this returns after process finishes execution
    try:
        await proc.communicate()
    except Exception:
        await proc.wait()
    except KeyboardInterrupt:
        proc.kill()

    # try:
    #     cp = run(
    #         cmd,
    #         timeout=timeout,
    #         shell=shell,
    #         check=check,
    #         text=text,
    #         stdout=PIPE,
    #         stderr=PIPE,
    #         bufsize=bufsize,
    #         executable="/usr/bin/zsh",
    #         **kwargs,
    #     )
    # except CalledProcessError as ce:
    #     return CompletedProcess(cmd, returncode=ce.returncode, stdout="", stderr="")
    # else:
    #     if not isinstance(cp.stdout, str):
    #         cp.stdout = ""
    #     return cp


async def test_long_cmd():
    cmd = """for (( i = 0; i < 3; i++ )); do echo "Current time: $(date +"%T")"; sleep 1; done"""
    await shell(cmd)


async def test_err_cmd():
    cmd = "cat non_existent_file.txt"
    await shell(cmd)


async def main():
    await test_err_cmd()


if __name__ == "__main__":
    asyncio.run(main())
