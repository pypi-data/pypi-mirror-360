import click
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@click.option('-v', '--volumes', type=bool, is_flag=True, help='Remove named volumes/configmaps declared in the "volumes"/"configs" sections')
@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
def down(*, helm, name, namespace, volumes, **_):
  ''' Like `docker-compose down` but stops the kubernetes deployed resources
  '''
  utils.run([
    *helm, 'uninstall',
    *(('-n', namespace) if namespace else tuple()),
    name,
  ])
  if volumes:
    from kube_compose.cli.volume.rm import rm as volume_rm
    from kube_compose.cli.configmap.rm import rm as configmap_rm
    volume_rm(volume=None)
    configmap_rm(configmap=None)
