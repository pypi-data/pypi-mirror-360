import click
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(helm='helm')
@utils.require_kube_compose_release
@click.argument('revision', type=int, required=False)
def rollback(revision, *, helm, name, namespace, **_):
  ''' Alias for `helm rollback [revision]`
  '''
  utils.run([
    *helm, 'rollback',
    *(('-n', namespace) if namespace else tuple()),
     name,
     *([revision] if revision else []),
  ])
