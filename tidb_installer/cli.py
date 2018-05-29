
"""Console script for tidb_installer."""

import os
import sys

import click

from .task import init_tidb_ansible, create_tidb_cluster, deploy_tidb_cluster


@click.group()
def main():
    pass


@main.command('init', help='init tidb installer environment.')
@click.option('--path', '-p', type=str, help='tidb installer work directory.')
@click.option('--version', '-v', type=str, help='tidb-ansible version.')
def init(**kwargs):
    """Init command."""
    path = kwargs['path']
    version = kwargs['version']
    if not all((path, version)):
        print('path and version are needed.')
        return

    init_tidb_ansible(path, version)


@main.command('create', help='create a Tidb cluster.')
@click.option('--path', '-f', help='Tidb installer work directory.')
@click.option('--host-type', type=click.Choice(['vagrant']), help='host machine type.')
@click.option('--skip-host/--no-skip-host', default=False, help='skip creating host machine.')
@click.option('--user', '-u', default='tidb', help='Tidb cluster system user name.')
@click.option('--tidb', '-d', multiple=True, help='Tidb host address.')
@click.option('--pd', '-p', multiple=True, help='Pd host address.')
@click.option('--tikv', '-k', multiple=True, help='Tikv host address.')
@click.option('-n', default=1, help='numbers of the Tikv instances.')
def create(**kwargs):
    """Create command."""
    path = kwargs['path']
    host_type = kwargs['host_type']
    skip_host = kwargs['skip_host']
    user = kwargs['user']
    tidb = kwargs['tidb']
    pd = kwargs['pd']
    tikv = kwargs['tikv']
    n = kwargs['n']

    if not path:
        print('installer work directory is needed.')
        return

    if not host_type:
        print('no host type is needed.')
        return

    if not all((tidb, pd, tikv)):
        print('tidb, pd, tikv servers are needed.')
        return

    os.chdir(path)
    path = os.getcwd()

    create_tidb_cluster(path, host_type, skip_host, tidb, pd, tikv)

    deploy_tidb_cluster(path)


if __name__ == "__main__":
    main()
