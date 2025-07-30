import click
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
@click.argument('service', type=str, required=False)
def stop(service, *, namespace, kubectl, docker_compose_config, **_):
  ''' Like `docker-compose stop` but effects the kubernetes deployed resources
  '''
  services = [service] if service is not None else docker_compose_config.get('services', {}).keys()
  utils.run([
    *kubectl, 'scale',
    *(('-n', namespace) if namespace else tuple()),
    '--replicas=0',
    *[f"deploy/{service}" for service in services],
  ])
