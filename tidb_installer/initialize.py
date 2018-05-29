
"""Initialize the tool dependency."""

import os

from .command import Command


__all__ = ['TidbAnsible']


class TidbAnsible:
    """Tidb ansible class."""

    git_url = 'https://github.com/pingcap/tidb-ansible.git'

    def __init__(self, work_dir, version):
        self._work_dir = work_dir
        self._version = version

    def initialize(self):
        """Initialize tidb ansible environment."""
        if not os.path.exists(self._work_dir):
            os.mkdir(self._work_dir)
        elif not os.path.isdir(self._work_dir):
            raise RuntimeError(
                'Path %s already exists, but it is not a directory.' % self._work_dir)

        os.chdir(self._work_dir)

        self._download()
        self._create_virtual_env()
        self._install()

    def _download(self):
        cmd = Command(
            'git clone -b release-{0} {1}'.format(self._version, self.git_url))
        cmd.run()

    def _create_virtual_env(self):
        cmd = Command('python3 -m venv v3')
        cmd.run()

    def _install(self):
        cmd = Command('./v3/bin/pip install -r ./tidb-ansible/requirements.txt')
        cmd.run()

    @property
    def exe_path(self):
        return '{0}/v3/bin/ansible'.format(self._work_dir)
