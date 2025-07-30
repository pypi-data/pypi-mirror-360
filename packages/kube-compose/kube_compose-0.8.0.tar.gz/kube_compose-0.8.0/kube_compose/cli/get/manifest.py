from kube_compose.cli.get import get
from kube_compose import utils

@get.command('manifest')
@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
def get_manifest(*, name, namespace, helm, **_):
  ''' download the manifest for a named release
  '''
  utils.run([*helm, 'get', 'manifest', *(('-n', namespace) if namespace else tuple()), name])
