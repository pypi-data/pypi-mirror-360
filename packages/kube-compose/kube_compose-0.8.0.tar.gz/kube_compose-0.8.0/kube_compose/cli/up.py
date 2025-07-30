import subprocess
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(helm='helm', kubectl='kubectl')
@utils.require_kube_compose_release
def up(*, helm, kubectl, name, namespace, docker_compose_config_raw, docker_compose_config, **_):
  ''' Like `docker-compose up` but runs in the kubernetes cluster
  '''
  from kube_compose.cli.volume.create import create as volume_create
  from kube_compose.cli.configmap.create import create as configmap_create
  volume_create(volume=None)
  configmap_create(configmap=None)
  if subprocess.call([
    *helm, 'status', *(('-n', namespace) if namespace else tuple()), name
  ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
    utils.run([
      *helm, 'upgrade',
      *(('-n', namespace) if namespace else tuple()),
      name,
      utils.helm_chart,
      '-f', '-'
    ], input=docker_compose_config_raw)
  else:
    utils.run([
      *helm, 'install',
      *(('-n', namespace) if namespace else tuple()),
      name,
      utils.helm_chart,
      '-f', '-',
    ], input=docker_compose_config_raw)
  #
  utils.run([
    *kubectl, 'rollout', 'status',
    *(('-n', namespace) if namespace else tuple()),
    *[f"deploy/{service}" for service in docker_compose_config.get('services', {})],
  ])
