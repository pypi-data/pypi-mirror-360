import yaml
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
def drift(*, kubectl, namespace, **_):
  ''' Compare the expected next deployment with the current deployment in kubernetes
  '''
  from kube_compose.cli.template import template
  utils.run([
    *kubectl, 'diff', *(('-n', namespace) if namespace else tuple()), '-f', '-'
  ], input=yaml.dump_all(template()).encode())
