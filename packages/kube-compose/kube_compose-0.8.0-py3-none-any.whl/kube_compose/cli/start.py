import click
import itertools
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
@click.argument('service', type=str, required=False)
def start(service, *, namespace, kubectl, docker_compose_config, **_):
  ''' Like `docker-compose start` but effects the kubernetes deployed resources
  '''
  if service is not None:
    replicas = docker_compose_config.get('services', {}).get(service, {}).get('deploy', {}).get('replicas', 1) or 1
    utils.run([
      *kubectl, 'scale',
      *(('-n', namespace) if namespace else tuple()),
      f"--replicas={replicas}",
      f"deploy/{service}",
    ])
  else:
    service_replicas = []
    for svc in docker_compose_config.get('services', {}).keys():
      replicas = docker_compose_config['services'][svc].get('deploy', {}).get('replicas', 1)
      service_replicas.append((replicas, svc))
    for replicas, svcs in itertools.groupby(sorted(service_replicas), lambda key: key[0]):
      utils.run([
        *kubectl, 'scale',
        *(('-n', namespace) if namespace else tuple()),
        f"--replicas={replicas}",
        *[f"deploy/{svc}" for svc in svcs],
      ])
