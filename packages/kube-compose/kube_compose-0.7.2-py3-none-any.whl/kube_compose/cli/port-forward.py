import click
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
@click.argument('service', type=str, required=True)
@click.argument('args', nargs=-1, type=str)
def port_forward(service, args, *, namespace, kubectl, **_):
  ''' port-forward service [local_port:]remote_port ...
  '''
  utils.run([
    *kubectl, 'port-forward',
    *(('-n', namespace) if namespace else tuple()),
    f"deploy/{service}",
    *args,
  ])
