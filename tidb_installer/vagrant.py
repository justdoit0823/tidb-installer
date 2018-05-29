
"""Vagrant management module."""

import os

from jinja2 import Template

from .command import Command


__all__ = ['Vagrant']


class Vagrant:
    """Vagrant machine node."""

    def __init__(self, user, host, work_dir):
        self._user = user
        self._host = host
        self._vbox_dir = work_dir

    def start(self):
        """Start machine node."""
        self._prepare()
        self._run()

    def _prepare(self):
        if not os.path.exists(self._vbox_dir):
            os.mkdir(self._vbox_dir)
        elif not os.path.isdir(self._vbox_dir):
            raise RuntimeError(
                'Path %s already exists, but it is not a directory.' % self._vbox_dir)

        os.chdir(self._vbox_dir)

        if not os.path.exists('Vagrantfile'):
            init_cmd = Command('vagrant init hashicorp/precise64')
            init_cmd.run()

        self._generate_file()

    def _run(self):
        cmd = Command('vagrant up')
        cmd.run()

    def _generate_file(self):
        temp_path = os.path.dirname(__file__) + '/' + 'vagrant.temp'
        with open(temp_path) as f:
            template = Template(f.read())
            vagrant_file = template.render(user=self._user, host=self._host)

        with open('Vagrantfile', 'w') as f:
            f.write(vagrant_file)
