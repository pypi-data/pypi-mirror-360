import json
import click
from kube_compose import utils
from kube_compose.cli.volume import volume

@volume.command('ls')
def _(**kwargs):
  ''' List kubernetes persistent volume claims
  '''
  ls(**kwargs)

@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
def ls(*, namespace, kubectl, **_):
  utils.run([
    *kubectl, 'get',
    *(('-n', namespace) if namespace else tuple()),
    'pvc',
  ])
