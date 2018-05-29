
"""Utils module."""

from contextlib import contextmanager
import os


__all__ = ['cwd']


@contextmanager
def cwd():
    """Restore current work directory context manager."""
    cur_cwd = os.getcwd()

    yield

    os.chdir(cur_cwd)
