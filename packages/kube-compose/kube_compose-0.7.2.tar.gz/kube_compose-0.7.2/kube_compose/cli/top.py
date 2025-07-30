import click
from datetime import datetime
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
@click.argument('service', type=str, required=False)
def top(service, *, namespace, docker_compose_config, kubectl, **_):
  ''' Like `docker-compose top` but show status of the kubernetes deployed resource
  '''
  import subprocess
  for svc in ([service] if service is not None else docker_compose_config.get('services', {}).keys()):
    print(svc)
    try:
      results = subprocess.check_output([
        *kubectl, 'exec', 
        *(('-n', namespace) if namespace else tuple()),
        f"deploy/{svc}",
        '--',
        '/bin/sh',
        '-c',
        'cat /proc/*/stat 2> /dev/null; exit 0'
      ])
    except subprocess.CalledProcessError as e:
      print('  Error checking processes')
    else:
      print(f"{'UID':>6}{'PID':>10}{'PPID':>10}{'C':>5}{'STIME':>8}{'TTY':>6}{'TIME':>11} {'CMD'}")
      for line in results.decode().splitlines():
        # https://man7.org/linux/man-pages/man5/proc.5.html
        (
          pid,
          comm,
          state,
          ppid,
          pgrp,
          session,
          tty_nr,
          tpgid,
          flags,
          minflt,
          cminflt,
          majflt,
          cmajflt,
          utime,
          stime,
          cutime,
          cstime,
          priority,
          nice,
          num_threads,
          itrealvalue,
          starttime,
          vsize,
          rss,
          rsslim,
          *_,
        ) = line.split(' ')
        print(f"{'?':>6}{pid:>10}{ppid:>10}{'?':>5}{starttime:>8}{'?':>6}{utime:>11} {comm[1:-1]}")
