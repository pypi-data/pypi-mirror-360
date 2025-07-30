from kube_compose.cli.get import get
from kube_compose import utils

@get.command('metadata')
@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
def metadata(*, name, namespace, helm, **_):
  ''' This command fetches metadata for a given release
  '''
  utils.run([*helm, 'get', 'metadata', *(('-n', namespace) if namespace else tuple()), name])
