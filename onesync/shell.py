import sys
import collections
import asyncio

from pathlib import Path

from asyncio.events import get_running_loop, AbstractEventLoop
from asyncio.unix_events import _UnixSelectorEventLoop
from asyncio.subprocess import SubprocessStreamProtocol
from asyncio.base_subprocess import BaseSubprocessTransport

from typing import Iterable, AsyncIterable, Literal

from onesync.interface import Pipeline, PopenPosixTypedDict

DEFAULT_STREAM_LIMIT: int = asyncio.streams._DEFAULT_LIMIT  # type: ignore

# sync version
# reff: https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
# You can direct the subprocess output to the streams directly. Simplified example:
# subprocess.run(['ls'], stderr=sys.stderr, stdout=sys.stdout)


def stream_protocol(output_limit, loop):
    return SubprocessStreamProtocol(limit=output_limit, loop=loop)


def sync_shell(
    cmd,
    stdout=None,
    stderr=None,
):
    import subprocess

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1)
    return process


def get_unix_running_loop() -> _UnixSelectorEventLoop:
    loop = get_running_loop()
    return loop  # type: ignore


class _UnsetParams:
    ...


UnsetParams = _UnsetParams()


class CommandGroup:
    def __init__(self, commands: str, keep_andif: bool = True):
        _cmds = self.parse_commands(commands, keep_andif)
        self._cmds = _cmds

    def __iter__(self):
        for cmd in self._cmds:
            yield cmd

    def __str__(self):
        return "\n".join(self)

    def __repr__(self):
        return self.__str__()

    def parse_commands(self, commands: str, keep_andif: bool):
        if not commands:
            raise ValueError("empty command")

        if keep_andif:
            _cmds = tuple(Command(cmd) for cmd in commands.split("\n") if cmd)
        else:
            _cmds = tuple(
                Command(cmd)
                for line in commands.split("\n")
                for cmd in line.split("&&")
                if cmd
            )
        return _cmds

    @property
    def commands(self):
        return self._cmds

    def andif(self):
        return " && ".join(self)


class Command(str):
    # default to linux
    def __new__(cls, string):
        if string.__class__ is cls:
            return string
        return super().__new__(cls, string.strip())

    def __repr__(self):
        return f"Command('{self}')"

    def andif(self, other):
        new = self + " && " + other
        return Command(new)


class CommandNode:
    def __init__(
        self,
        cmd: str,
        prev: "CommandNode | None" = None,
        next: "CommandNode | None" = None,
    ):
        self.cmd = Command(cmd)
        self.prev = prev
        self.next = next

    def __repr__(self):
        return f"CommandNode('{self.cmd}')"


class CommandChain:
    def __init__(self, head: CommandNode | None = None):
        self.head = head
        self.tail = head.next if head else None
        self._last_executed = None

    def insert(self, cmd: Command | str):
        node = CommandNode(cmd)

        if not self.head:
            self.head = node
            return

        self.head.prev, node.next = node, self.head

    def append(self, cmd: Command | str):
        node = CommandNode(cmd)

        if not self.head:
            self.head = node
            return

        cursor = self.head
        while cursor.next:
            cursor = cursor.next

        cursor.next, node.prev = node, cursor

    @classmethod
    def from_list(cls, cmd_list: list[str]):
        chain = cls()

        if (size := len(cmd_list)) < 3:
            for cmd in cmd_list:
                chain.append(cmd)
            return chain

        ptr = 0
        while ptr < size - 1:
            cur, next = CommandNode(cmd_list[ptr]), CommandNode(cmd_list[ptr + 1])
            if not chain.head:
                chain.head = cur
            cur.next, next.prev = next, cur
            ptr += 1

        return chain


class Screen:
    def __init__(self, max_lines: int = 2**16, text: bool = False):
        self._queue = collections.deque(maxlen=max_lines)
        self._text = text
        self._line_cursor = 0

    async def load(self, lines: Iterable | AsyncIterable):
        match lines:
            case collections.abc.Iterable():  # type: ignore
                for l in lines:
                    self.append(l)
            case collections.abc.AsyncIterable():  # type: ignore
                async for l in lines:
                    self.append(l)
            case _:
                raise TypeError("Expected Iterable or AsyncIterable")

    def append(self, line: bytes):
        self._queue.append(line)
        sys.stdout.write(line.decode())

    def __str__(self):
        return b"".join(self._queue).decode()

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            data = self._queue[self._line_cursor]
        except IndexError:
            raise StopIteration
        self._line_cursor += 1
        return data


class PosixProcess:
    def __init__(
        self,
        executable: str | None = None,
        stdin: Pipeline = -1,
        stdout: Pipeline = -1,
        stderr: Pipeline = -1,
        close_fds: bool = True,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        errors: str | None = None,
        startupinfo=None,
        creationflags: int = 0,
        restore_signals: bool = True,
        start_new_session: bool = False,
        pass_fds=(),
        *,
        user=None,
        group=None,
        extra_groups=None,
        umask: int = -1,
        pipesize: int = -1,
        process_group=None,
        output_limit: int = 0,
    ):
        self.reuse_args = PopenPosixTypedDict(
            bufsize=0,
            executable=executable,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            close_fds=close_fds,
            shell=True,
            cwd=cwd,
            env=env,
            text=False,
            encoding=None,
            errors=errors,
            startupinfo=startupinfo,
            creationflags=creationflags,
            restore_signals=restore_signals,
            start_new_session=start_new_session,
            pass_fds=pass_fds,
            user=user,
            group=group,
            extra_groups=extra_groups,
            umask=umask,
            pipesize=pipesize,
            process_group=process_group,
        )  # type: ignore

        self.output_limit = output_limit or asyncio.streams._DEFAULT_LIMIT  # type: ignore
        self._screen = Screen(max_lines=self.output_limit)

    async def execute(self, cmd: str, timeout: int = 60):
        loop = asyncio.events.get_running_loop()
        protocol = SubprocessStreamProtocol(self.output_limit, loop)

        transport = await loop._make_subprocess_transport(
            protocol, cmd, **self.reuse_args
        )  # type: ignore

        stdout = asyncio.wait_for(self.read_stream(transport, protocol, 1), timeout)
        stderr = asyncio.wait_for(self.read_stream(transport, protocol, 2), timeout)

        await asyncio.gather(stdout, stderr)

        return ProcessResult(transport, str(self._screen))

    async def read_stream(
        self,
        transport: BaseSubprocessTransport,
        protocol: SubprocessStreamProtocol,
        fd: Literal[1, 2],
    ):
        if fd == 1:
            stream = protocol.stdout
        elif fd == 2:
            stream = protocol.stderr
        else:
            raise ValueError("fd has to be 1 or 2")

        if not stream:
            return

        await self._screen.load(stream)

        pipe_tp = transport.get_pipe_transport(fd)
        if not pipe_tp:
            raise

        pipe_tp.close()

    def update_args(self, **kwargs):
        EXCLUDED_PARAMS = {"shell", "buffsize", "text", "encoding"}
        keys = kwargs.keys()

        if fixed_params := (keys & EXCLUDED_PARAMS):
            raise Exception(f"Fixed params {fixed_params}")

        if invalid_params := (keys - PopenPosixTypedDict.__annotations__.keys()):
            raise Exception(f"Invalid params {invalid_params}")

        self.reuse_args.update(kwargs)  # type: ignore


class ProcessResult:
    def __init__(self, transport: BaseSubprocessTransport, content: str):
        self._transport = transport
        self._content = content
        self.returncode = transport.get_returncode()
        self._pid = -1

    def __str__(self):
        return f"ProcessResult<pid={self.pid}, returncode={self.returncode}>"

    def __repr__(self):
        return str(self)

    async def wait(self):
        """Wait until the process exit and return the process return code."""
        return await self._transport._wait()

    def send_signal(self, signal):
        self._transport.send_signal(signal)

    def terminate(self):
        self._transport.terminate()

    def kill(self):
        self._transport.kill()

    @property
    def pid(self):
        if not self._pid:
            self._pid = self._transport.get_pid()
        return self._pid

    @property
    def content(self):
        return self._content


class Shell:
    def __init__(
        self,
        loop: AbstractEventLoop,
        process: PosixProcess,
        executable: Path | None = None,
    ):
        self.loop = loop
        self.process = process
        self.executeable = executable

    async def __call__(self, command, *, timeout: int = 60):
        return await self.process.execute(command, timeout)

    async def install(self, mod):
        raise NotImplementedError


class Zshell(Shell):
    def __init__(
        self,
        loop: AbstractEventLoop,
        process: PosixProcess,
        executable: Path = Path("/usr/bin/zsh"),
    ):
        super().__init__(loop, process, executable)
        self.process.update_args(executable=executable)

    async def install(self, mod):
        return await mod.install(shell=self)


def shell_factory(**kwargs) -> Shell:
    loop = asyncio.get_event_loop()
    process = PosixProcess(**kwargs)
    return Zshell(loop, process)


shell = shell_factory()
