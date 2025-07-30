import click
from kube_compose import utils
from kube_compose.cli.volume import volume

@volume.command('inspect')
@click.argument('volume', type=str, required=True)
def _(**kwargs):
  ''' Inspect a kubernetes persistent volume
  '''
  inspect(**kwargs)

@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
def inspect(*, volume, namespace, kubectl, **_):
  utils.run([
    *kubectl, 'get',
    *(('-n', namespace) if namespace else tuple()),
    f"pvc/{volume}",
    '-o', 'yaml',
  ])
