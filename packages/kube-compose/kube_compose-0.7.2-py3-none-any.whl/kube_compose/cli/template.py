import sys
import yaml
from kube_compose.cli import cli
from kube_compose import utils

@cli.command('template')
def _(**_):
  ''' Alias for `helm template [release]`
  '''
  from kube_compose.cli.volume.template import template as volume_create_template
  from kube_compose.cli.configmap.template import template as configmap_create_template
  yaml.dump_all([
    *volume_create_template(volume=None),
    *configmap_create_template(configmap=None),
    *template(),
  ], sys.stdout)

@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
def template(*, helm, name, namespace, docker_compose_config_raw, **_):
  output = list(yaml.safe_load_all(utils.check_output([
    *helm, 'template',
    *(('-n', namespace) if namespace else tuple()),
    name,
    utils.helm_chart,
    '-f', '-', '--validate=false',
  ], input=docker_compose_config_raw)))
  return output
