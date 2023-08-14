import asyncio
from asyncio.events import get_event_loop, get_running_loop, AbstractEventLoop
from asyncio.unix_events import _UnixSelectorEventLoop
from asyncio.protocols import BaseProtocol

from asyncio.base_subprocess import BaseSubprocessTransport


from asyncio.subprocess import Process, SubprocessStreamProtocol, create_subprocess_shell, PIPE
from asyncio.streams import StreamReader, StreamWriter

from io import StringIO

import collections
from typing import Iterable, AsyncIterable


class Screen:
    def __init__(self, max_lines: int = 100):
        self._queue = collections.deque(maxlen=max_lines)
    
    async def load(self, lines: Iterable| AsyncIterable):
        match lines:
            case collections.abc.Iterable(): # type: ignore
                for l in lines:
                    self._queue.append(l)
            case collections.abc.AsyncIterable(): # type: ignore
                async for l in lines:
                    self._queue.append(l)
            case _:
                raise TypeError("Expected Iterable or AsyncIterable")

    def append(self, line: str):
        self._queue.append(line)

    def __str__(self):
        return "".join(self._queue)

    def __iter__(self):
        for line in self._queue:
            yield line
    

class MyProcess:
    def __init__(self, transport: BaseSubprocessTransport, protocol: SubprocessStreamProtocol, loop: AbstractEventLoop):
        self._transport = transport
        self._protocol = protocol
        self._loop = loop

        # self.stdin = protocol.stdin
        # self.stdout = protocol.stdout
        # self.stderr = protocol.stderr
        self.pid = transport.get_pid()

    async def read_output(self):
        if not self._protocol.stdout:
            return

        async for line in self._protocol.stdout:
            yield line.decode()

    async def read_stdout(self):
        async for line in self.read_output():
            print(line)
    

async def main():
    limit = asyncio.streams._DEFAULT_LIMIT
    loop = asyncio.events.get_running_loop()
    protocol_factory = lambda: SubprocessStreamProtocol(limit=limit,
                                                        loop=loop)
    cmd = 'ls -l'

    transport, protocol = await loop.subprocess_shell(
        protocol_factory,
        cmd,
        )

    p = Process
    p.communicate()

    proc = MyProcess(transport, protocol, loop)
    std_out = proc.read_stdout()

    proc._transport._wait

    read_pipe = transport.get_pipe_transport(1)

# this 

from subprocess import run

asyncio.run(main())

