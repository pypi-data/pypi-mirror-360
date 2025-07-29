import contextlib
import io
import os

import pytest

from yib import yconsole


def _get_tty_compatible_console() -> yconsole.Console:
    environ = os.environ.copy()
    environ["TTY_COMPATIBLE"] = "1"
    return yconsole.Console(stderr=True, _environ=environ)


def test_fatal():
    console = yconsole.Console()
    with pytest.raises(SystemExit):
        console.fatal("This is a fatal message.")


def test_warning():
    console = _get_tty_compatible_console()
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        console.warning("This is a warning")
    assert buf.getvalue() == "\x1b[33mWARNING:\x1b[0m This is a warning\n"


def test_error():
    console = _get_tty_compatible_console()
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        console.error("This is a error")
    assert buf.getvalue() == "\x1b[31mERROR:\x1b[0m This is a error\n"
