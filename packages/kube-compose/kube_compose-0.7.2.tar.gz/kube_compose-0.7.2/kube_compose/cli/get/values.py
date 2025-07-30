from kube_compose.cli.get import get
from kube_compose import utils

@get.command('values')
@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
def values(*, name, namespace, helm, **_):
  ''' download the values file for a named release
  '''
  utils.run([*helm, 'get', 'values', *(('-n', namespace) if namespace else tuple()), name])
