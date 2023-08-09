from typing import Literal, Callable, TypedDict

"""
Here are the possible values for stdin and stdout:


1. None (default): The input/output streams will be inherited from the parent process.
2. subprocess.PIPE: A new pipe will be created for the input/output stream, allowing communication between the parent and child processes via the pipe.
3. A file descriptor: You can provide a file descriptor (an integer) for the input/output stream, e.g., 1 for standard output or 2 for standard error.


NOTE: when using PIPE,  A new pipe will be created using
stdin, stdin_w = socket.socketpair()
"""
Pipeline = Literal[1, 2, -1, None]


class PopenTypedDict(TypedDict):
    args: str | list
    bufsize: int
    executable: str | None
    stdin: Pipeline
    stdout: Pipeline
    stderr: Pipeline
    close_fds: bool
    shell: bool
    cwd: str | None
    env: dict[str, str] | None
    text: bool
    universal_newlines: bool
    encoding: str | None
    errors: str | None


class PopoenWindowsTypedDict(PopenTypedDict):
    startupinfo: ...
    creationflags: ...


class PopenPosixTypedDict(PopenTypedDict):
    preexec_fn: Callable | None
    restore_signals: bool
    start_new_session: bool
    process_group: int
    group: int
    extra_groups: list[int]
    user: int
    umask: int
    pass_fds: list[int]
