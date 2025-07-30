import click
import itertools
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
@click.argument('args', nargs=-1, type=str)
def scale(args, *, namespace, kubectl, **_):
  ''' Like `docker-compose scale` but effects the kubernetes deployed resources
  Arguments are expected to be like: `service-name=replicas`
  '''
  service_replicas = []
  for arg in args:
    svc, _, replicas = arg.partition('=')
    service_replicas.append((int(replicas), svc))
  for replicas, svcs in itertools.groupby(sorted(service_replicas), lambda key: key[0]):
    utils.run([
      *kubectl, 'scale',
      *(('-n', namespace) if namespace else tuple()),
      f"--replicas={replicas}",
      *[f"deploy/{svc}" for _, svc in svcs],
    ])
