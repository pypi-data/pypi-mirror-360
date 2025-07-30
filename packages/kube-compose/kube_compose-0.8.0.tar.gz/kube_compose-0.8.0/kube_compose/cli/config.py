from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
def config(*, helm, name, namespace, **_):
  ''' Like `docker-compose config` but shows the kubernetes deployed config
  '''
  utils.run([
    *helm, 'get', 'values',
    *(('-n', namespace,) if namespace else tuple()),
    name,
  ])
