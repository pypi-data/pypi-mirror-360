import json
import click
from kube_compose import utils
from kube_compose.cli import cli

@cli.command(context_settings={"ignore_unknown_options": True})
@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
@click.argument('args', nargs=-1, type=str, metavar='[SERVICE:SRC_PATH|SRC_PATH|-] [DEST_PATH|-|SERVICE:DEST_PATH]')
def cp(*, args, namespace, kubectl, **_):
  ''' Like `docker-compose cp` but for the kubernetes deployed resources
  '''
  args_ = []
  for arg in args:
    if ':' in arg:
      service, _, path = arg.partition(':')
      # find the pod for the specified docker-compose service
      pod = utils.check_output([
        *kubectl, 'get', 'pod',
        *(['-n', namespace] if namespace else []),
        '-l', f"app.kubernetes.io/name={service}", '-o', 'jsonpath="{.items[0][\'metadata.name\']}"'
      ])
      args_.append(
        (f"{namespace}/" if namespace else '')
        + f"{json.loads(pod.decode())}:{path}"
      )
    else:
      args_.append(arg)
  utils.run([*kubectl, 'cp', *args_])
