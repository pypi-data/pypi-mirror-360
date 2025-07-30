from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
def status(*, helm, name, namespace, **_):
  ''' Alias for `helm status [release]`
  '''
  utils.run([
    *helm, 'status',
    *(('-n', namespace) if namespace else tuple()),
     name,
  ])
