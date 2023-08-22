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


class AsyncioPopen(TypedDict):
    executable: str | None
    stdin: Pipeline
    stdout: Pipeline
    stderr: Pipeline
    close_fds: bool
    cwd: str | None
    env: dict[str, str] | None
    errors: str | None


class PopenTypedDict(AsyncioPopen):
    """
    args: A string, or a sequence of program arguments.

    bufsize: supplied as the buffering argument to the open() function when
        creating the stdin/stdout/stderr pipe file objects

    executable: A replacement program to execute.

    stdin, stdout and stderr: These specify the executed programs' standard
        input, standard output and standard error file handles, respectively.

    preexec_fn: (POSIX only) An object to be called in the child process
        just before the child is executed.

    close_fds: Controls closing or inheriting of file descriptors.

    shell: If true, the command will be executed through the shell.

    cwd: Sets the current directory before the child is executed.

    env: Defines the environment variables for the new process.

    text: If true, decode stdin, stdout and stderr using the given encoding
        (if set) or the system default otherwise.

    universal_newlines: Alias of text, provided for backwards compatibility.

    startupinfo and creationflags (Windows only)

    restore_signals (POSIX only)

    start_new_session (POSIX only)

    process_group (POSIX only)

    group (POSIX only)

    extra_groups (POSIX only)

    user (POSIX only)

    umask (POSIX only)

    pass_fds (POSIX only)

    encoding and errors: Text mode encoding and error handling to use for
        file objects stdin, stdout and stderr.
    """

    args: str | list
    bufsize: int
    shell: bool
    text: bool
    universal_newlines: bool
    encoding: str | None


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
