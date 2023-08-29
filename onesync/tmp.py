import os

"""
this is a short code snippet from sh that constructs the OProc object
which is used to run the command.
NOTE: https://github.com/amoffat/sh/blob/develop/sh.py#L247
https://sh.readthedocs.io/en/latest/sections/asynchronous_execution.html#asyncio
"""


def proc(
    self,
    command,
    parent_log,
    cmd,
    stdin,
    stdout,
    stderr,
    call_args,
    pipe,
    process_assign_lock,
):
    """
    cmd is the full list of arguments that will be exec'd.  it includes the program
    name and all its arguments.

    stdin, stdout, stderr are what the child will use for standard input/output/err.

    call_args is a mapping of all the special keyword arguments to apply to the
    child process.
    """
    self.command = command
    self.call_args = call_args

    # convenience
    ca = self.call_args

    if ca["uid"] is not None:
        if os.getuid() != 0:
            raise RuntimeError("UID setting requires root privileges")

        target_uid = ca["uid"]

        pwrec = pwd.getpwuid(ca["uid"])
        target_gid = pwrec.pw_gid
    else:
        target_uid, target_gid = None, None

    if ca["piped"]:
        ca["tty_out"] = False

    self._stdin_process = None

    stdin_is_fd_based = ob_is_fd_based(stdin)
    stdout_is_fd_based = ob_is_fd_based(stdout)
    stderr_is_fd_based = ob_is_fd_based(stderr)

    if isinstance(ca["tee"], (str, bool, int)) or ca["tee"] is None:
        tee = {ca["tee"]}
    else:
        tee = set(ca["tee"])
    tee_out = TEE_STDOUT.intersection(tee)
    tee_err = TEE_STDERR.intersection(tee)

    single_tty = ca["tty_in"] and ca["tty_out"] and ca["unify_ttys"]

    if single_tty:
        self._stdin_parent_fd, self._stdin_child_fd = pty.openpty()
        self._stdout_parent_fd = os.dup(self._stdin_parent_fd)
        self._stdout_child_fd = os.dup(self._stdin_child_fd)
        self._stderr_parent_fd = os.dup(self._stdin_parent_fd)
        self._stderr_child_fd = os.dup(self._stdin_child_fd)
    else:
        if isinstance(stdin, OProc) and stdin.call_args["piped"]:
            self._stdin_child_fd = stdin._pipe_fd
            self._stdin_parent_fd = None
            self._stdin_process = stdin
        elif stdin_is_fd_based:
            self._stdin_child_fd = os.dup(get_fileno(stdin))
            self._stdin_parent_fd = None
        elif ca["tty_in"]:
            self._stdin_parent_fd, self._stdin_child_fd = pty.openpty()
        else:
            self._stdin_child_fd, self._stdin_parent_fd = os.pipe()
        if stdout_is_fd_based and not tee_out:
            self._stdout_child_fd = os.dup(get_fileno(stdout))
            self._stdout_parent_fd = None
        elif ca["tty_out"]:
            self._stdout_parent_fd, self._stdout_child_fd = pty.openpty()
        else:
            self._stdout_parent_fd, self._stdout_child_fd = os.pipe()
        if stderr is OProc.STDOUT:
            if stdout_is_fd_based and not tee_out:
                self._stderr_parent_fd = None
            else:
                self._stderr_parent_fd = os.dup(self._stdout_parent_fd)
            self._stderr_child_fd = os.dup(self._stdout_child_fd)

        elif stderr_is_fd_based and not tee_err:
            self._stderr_child_fd = os.dup(get_fileno(stderr))
            self._stderr_parent_fd = None

        else:
            self._stderr_parent_fd, self._stderr_child_fd = os.pipe()

    piped = ca["piped"]
    self._pipe_fd = None
    if piped:
        fd_to_use = self._stdout_parent_fd
        if piped == "err":
            fd_to_use = self._stderr_parent_fd
        self._pipe_fd = os.dup(fd_to_use)

    new_session = ca["new_session"]
    new_group = ca["new_group"]
    needs_ctty = ca["tty_in"]
    if needs_ctty:
        new_session = True

    self.ctty = None
    if needs_ctty:
        self.ctty = os.ttyname(self._stdin_child_fd)

    gc_enabled = gc.isenabled()
    if gc_enabled:
        gc.disable()

    session_pipe_read, session_pipe_write = os.pipe()
    exc_pipe_read, exc_pipe_write = os.pipe()

    if IS_MACOS:
        close_pipe_read, close_pipe_write = os.pipe()
    else:
        close_pipe_read, close_pipe_write = None, None

    self.sid = None
    self.pgid = None
    self.pid = os.fork()

    if self.pid == 0:  # pragma: no cover
        if IS_MACOS:
            os.read(close_pipe_read, 1)
            os.close(close_pipe_read)
            os.close(close_pipe_write)

        flags = fcntl.fcntl(exc_pipe_write, fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(exc_pipe_write, fcntl.F_SETFD, flags)

        try:
            if ca["bg"] is True:
                signal.signal(signal.SIGHUP, signal.SIG_IGN)

            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

            if new_session:
                os.setsid()
            elif new_group:
                os.setpgid(0, 0)

            sid = os.getsid(0)
            pgid = os.getpgid(0)
            payload = (f"{sid},{pgid}").encode(DEFAULT_ENCODING)
            os.write(session_pipe_write, payload)

            if ca["tty_out"] and not stdout_is_fd_based and not single_tty:
                tty.setraw(self._stdout_child_fd)
            if self._stdin_parent_fd:
                os.close(self._stdin_parent_fd)
            if self._stdout_parent_fd:
                os.close(self._stdout_parent_fd)
            if self._stderr_parent_fd:
                os.close(self._stderr_parent_fd)

            os.close(session_pipe_read)
            os.close(exc_pipe_read)

            cwd = ca["cwd"]
            if cwd:
                os.chdir(cwd)

            os.dup2(self._stdin_child_fd, 0)
            os.dup2(self._stdout_child_fd, 1)
            os.dup2(self._stderr_child_fd, 2)
            if needs_ctty:
                tmp_fd = os.open(os.ttyname(0), os.O_RDWR)
                os.close(tmp_fd)

            if ca["tty_out"] and not stdout_is_fd_based:
                setwinsize(1, ca["tty_size"])

            if ca["uid"] is not None:
                os.setgid(target_gid)
                os.setuid(target_uid)

            preexec_fn = ca["preexec_fn"]
            if callable(preexec_fn):
                preexec_fn()

            close_fds = ca["close_fds"]
            if ca["pass_fds"]:
                close_fds = True

            if close_fds:
                pass_fds = {0, 1, 2, exc_pipe_write}
                pass_fds.update(ca["pass_fds"])

                try:
                    inherited_fds = os.listdir("/dev/fd")
                except (IOError, OSError):
                    inherited_fds = os.listdir("/proc/self/fd")
                inherited_fds = set(int(fd) for fd in inherited_fds) - pass_fds
                for fd in inherited_fds:
                    try:
                        os.close(fd)
                    except OSError:
                        pass
            bytes_cmd = [c.encode(ca["encoding"]) for c in cmd]
            if ca["env"] is None:
                os.execv(bytes_cmd[0], bytes_cmd)
            else:
                os.execve(bytes_cmd[0], bytes_cmd, ca["env"])

        except Exception:  # noqa: E722
            tb = traceback.format_exc().encode("utf8", "ignore")

            try:
                os.write(exc_pipe_write, tb)

            except Exception as e:
                sys.stderr.write(f"\nFATAL SH ERROR: {e}\n")

            finally:
                os._exit(255)

    # parent
    else:
        if gc_enabled:
            gc.enable()
        os.close(self._stdin_child_fd)
        os.close(self._stdout_child_fd)
        os.close(self._stderr_child_fd)
        if IS_MACOS:
            os.close(close_pipe_read)
            os.write(close_pipe_write, str(1).encode(DEFAULT_ENCODING))
            os.close(close_pipe_write)

        os.close(exc_pipe_write)
        fork_exc = os.read(exc_pipe_read, 1024**2)
        os.close(exc_pipe_read)
        if fork_exc:
            fork_exc = fork_exc.decode(DEFAULT_ENCODING)
            raise ForkException(fork_exc)

        os.close(session_pipe_write)
        sid, pgid = os.read(session_pipe_read, 1024).decode(DEFAULT_ENCODING).split(",")
        os.close(session_pipe_read)
        self.sid = int(sid)
        self.pgid = int(pgid)
        self.timed_out = False
        self.started = time.time()
        self.cmd = cmd
        self.exit_code = None
        self.stdin = stdin
        if callable(ca["out"]) and self.stdin is None:
            self.stdin = Queue()
        self._pipe_queue = Queue()
        self._wait_lock = threading.Lock()
        self._stdout = deque(maxlen=ca["internal_bufsize"])
        self._stderr = deque(maxlen=ca["internal_bufsize"])
        if ca["tty_in"] and not stdin_is_fd_based:
            setwinsize(self._stdin_parent_fd, ca["tty_size"])

        self.log = parent_log.get_child("process", repr(self))

        self.log.debug("started process")

        if ca["tty_in"] and not stdin_is_fd_based:
            attr = termios.tcgetattr(self._stdin_parent_fd)
            attr[3] &= ~termios.ECHO
            termios.tcsetattr(self._stdin_parent_fd, termios.TCSANOW, attr)

        self._stdin_stream = None
        if self._stdin_parent_fd:
            log = self.log.get_child("streamwriter", "stdin")
            self._stdin_stream = StreamWriter(
                log,
                self._stdin_parent_fd,
                self.stdin,
                ca["in_bufsize"],
                ca["encoding"],
                ca["tty_in"],
            )

        stdout_pipe = None
        if pipe is OProc.STDOUT and not ca["no_pipe"]:
            stdout_pipe = self._pipe_queue

        save_stdout = not ca["no_out"] and (tee_out or stdout is None)
        pipe_out = ca["piped"] in ("out", True)
        pipe_err = ca["piped"] in ("err",)

        self._stdout_stream = None
        if not pipe_out and self._stdout_parent_fd:
            if callable(stdout):
                stdout = construct_streamreader_callback(self, stdout)
            self._stdout_stream = StreamReader(
                self.log.get_child("streamreader", "stdout"),
                self._stdout_parent_fd,
                stdout,
                self._stdout,
                ca["out_bufsize"],
                ca["encoding"],
                ca["decode_errors"],
                stdout_pipe,
                save_data=save_stdout,
            )

        elif self._stdout_parent_fd:
            os.close(self._stdout_parent_fd)

        self._stderr_stream = None
        if (
            stderr is not OProc.STDOUT
            and not single_tty
            and not pipe_err
            and self._stderr_parent_fd
        ):
            stderr_pipe = None
            if pipe is OProc.STDERR and not ca["no_pipe"]:
                stderr_pipe = self._pipe_queue

            save_stderr = not ca["no_err"] and (tee_err or stderr is None)

            if callable(stderr):
                stderr = construct_streamreader_callback(self, stderr)

            self._stderr_stream = StreamReader(
                Logger("streamreader"),
                self._stderr_parent_fd,
                stderr,
                self._stderr,
                ca["err_bufsize"],
                ca["encoding"],
                ca["decode_errors"],
                stderr_pipe,
                save_data=save_stderr,
            )

        elif self._stderr_parent_fd:
            os.close(self._stderr_parent_fd)

        def timeout_fn():
            self.timed_out = True
            self.signal(ca["timeout_signal"])

        self._timeout_event = None
        self._timeout_timer = None
        if ca["timeout"]:
            self._timeout_event = threading.Event()
            self._timeout_timer = threading.Timer(
                ca["timeout"], self._timeout_event.set
            )
            self._timeout_timer.start()

        handle_exit_code = None
        if not self.command._spawned_and_waited and ca["bg_exc"] and not ca["async"]:

            def fn(exit_code):
                with process_assign_lock:
                    return self.command.handle_command_exit_code(exit_code)

            handle_exit_code = fn

        self._quit_threads = threading.Event()

        thread_name = f"background thread for pid {self.pid}"
        self._bg_thread_exc_queue = Queue(1)
        self._background_thread = _start_daemon_thread(
            background_thread,
            thread_name,
            self._bg_thread_exc_queue,
            timeout_fn,
            self._timeout_event,
            handle_exit_code,
            self.is_alive,
            self._quit_threads,
        )

        self._input_thread = None
        self._input_thread_exc_queue = Queue(1)
        if self._stdin_stream:
            close_before_term = not needs_ctty
            thread_name = f"STDIN thread for pid {self.pid}"
            self._input_thread = _start_daemon_thread(
                input_thread,
                thread_name,
                self._input_thread_exc_queue,
                self.log,
                self._stdin_stream,
                self.is_alive,
                self._quit_threads,
                close_before_term,
            )

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:

            def output_complete():
                pass

        else:

            def output_complete():
                loop.call_soon_threadsafe(self.command.aio_output_complete.set)

        self._output_thread_exc_queue = Queue(1)
        thread_name = f"STDOUT/ERR thread for pid {self.pid}"
        self._output_thread = _start_daemon_thread(
            output_thread,
            thread_name,
            self._output_thread_exc_queue,
            self.log,
            self._stdout_stream,
            self._stderr_stream,
            self._timeout_event,
            self.is_alive,
            self._quit_threads,
            self._stop_output_event,
            output_complete,
        )
