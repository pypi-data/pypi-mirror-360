from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
def history(*, helm, name, namespace, **_):
  ''' Alias for `helm history [release]`
  '''
  utils.run([
    *helm, 'history',
    *(('-n', namespace) if namespace else tuple()),
     name,
  ])
