
"""Tidb management commands based on ansible playbook."""

import os


__all__ = ['Command']


class Command:

    __slots__ = ('_cmd',)

    def __init__(self, cmd):
        self._cmd = cmd

    def run(self):
        """Execute the command."""
        if os.system(self._cmd) != 0:
            raise RuntimeError
