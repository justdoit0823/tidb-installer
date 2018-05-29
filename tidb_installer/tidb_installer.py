
"""Main module."""

import os

from jinja2 import Template

from .command import Command
from .initialize import TidbAnsible
from .utils import cwd
from .vagrant import Vagrant


__all__ = [
    'init_tidb_ansible', 'create_vagrant_machine', 'create_tidb_cluster',
    'deploy_tidb_cluster']


def init_tidb_ansible(work_dir, version):
    """Initialize tidb ansible environment."""
    with cwd():
        ansible = TidbAnsible(work_dir, version)
        ansible.initialize()
        print('Tidb ansible exe path %s.' % ansible.exe_path)


def create_vagrant_machine(work_dir, hosts, user='vagrant'):
    """Create machine based on vagrant."""
    print('{0}/vbox'.format(work_dir))
    if not os.path.exists('{0}/vbox'.format(work_dir)):
        os.mkdir('vbox')

    with cwd():
        for idx, host in enumerate(hosts):
            v_host = Vagrant(user, host, '{0}/vbox/{1}'.format(work_dir, host))
            v_host.start()


def generate_inventory(
        user, work_dir, tidb_hosts, pd_hosts, tikv_hosts,
        monitoring_hosts, grafana_hosts,
        alert_hosts, instance_num=1):
    """Generate deploy inventory."""
    monitored_hosts = set(
        tidb_hosts + pd_hosts + tikv_hosts + monitoring_hosts + grafana_hosts
        + alert_hosts)

    temp_path = os.path.dirname(__file__) + '/' + 'inventory.temp'
    with open(temp_path) as f:
        template = Template(f.read())
        inventory_content = template.render(
            user=user, tidb_hosts=tidb_hosts, pd_hosts=pd_hosts,
            tikv_hosts=tikv_hosts, monitoring_hosts=monitoring_hosts,
            grafana_hosts=grafana_hosts, alert_hosts=alert_hosts,
            monitored_hosts=monitored_hosts)

    inventory_file = work_dir + '/inventory'
    with open(inventory_file, 'w') as f:
        f.write(inventory_content)


def configure_ssh(work_dir, user, hosts):
    """Configure ssh connection."""
    configured_hosts = []
    with open(os.path.expanduser('~/.ssh/config')) as f:
        for line in f:
            if 'Host' not in line:
                continue

            for host in hosts:
                if host in line:
                    configured_hosts.append(host)

    new_hosts = tuple(set(hosts) - set(configured_hosts))
    new_configs = []
    for host in new_hosts:
        with cwd():
            os.chdir('{0}/vbox/{1}'.format(work_dir, host))
            cmd = Command('vagrant ssh-config > /tmp/ssh-config-{0}'.format(host))
            cmd.run()
            with open('/tmp/ssh-config-{0}'.format(host)) as f:
                content = f.read()
                content = content.replace('Host default', 'Host {0}'.format(host))
                new_configs.append(content)

    config_content = '\n'.join(new_configs)

    with open(os.path.expanduser('~/.ssh/config'), 'a') as f:
        f.write('\n\n' + config_content)


def create_tidb_cluster(
        work_dir, host_type, skip_host, tidb_hosts, pd_hosts, tikv_hosts,
        user='vagrant'):
    """Create tidb cluster machines."""
    uniq_hosts = set(tidb_hosts + pd_hosts + tikv_hosts)
    if not skip_host:
        create_vagrant_machine(work_dir, uniq_hosts, user=user)

    configure_ssh(work_dir, user, uniq_hosts)

    generate_inventory(
        user, work_dir, tidb_hosts, pd_hosts, tikv_hosts, (tidb_hosts[0],),
        (tidb_hosts[0],), (tidb_hosts[0],))


def deploy_tidb_cluster(work_dir):
    """Deploy tidb cluster."""
    ansible_base_path = '{0}/v3/bin'.format(work_dir)
    tidb_ansible_path = '{0}/tidb-ansible'.format(work_dir)
    prepare_cmd = Command('{0}/ansible-playbook -i {1}/iventory {2}/local_prepare.yml'.format(ansible_base_path, work_dir, tidb_ansible_path))
    prepare_cmd.run()

    bootstrap_cmd = Command('{0}/ansible-playbook -i {1}/iventory {2}/bootstrap.yml'.format(ansible_base_path, work_dir, tidb_ansible_path))
    bootstrap_cmd.run()

    deploy_cmd = Command('{0}/ansible-playbook -i {1}/iventory {2}/deploy.yml'.format(ansible_base_path, work_dir, tidb_ansible_path))
    deploy_cmd.run()

    start_cmd = Command('{0}/ansible-playbook -i {1}/iventory {2}/start.yml'.format(ansible_base_path, work_dir, tidb_ansible_path))
    start_cmd.run()
