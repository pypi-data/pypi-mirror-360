from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
def ps(*, name, namespace, helm, **_):
  ''' Like `docker-compose ps` but show status of the kubernetes deployed resource
  '''
  utils.run([
    *helm, 'status',
    *(('-n', namespace) if namespace else tuple()),
    name,
    '--show-resources',
  ])
