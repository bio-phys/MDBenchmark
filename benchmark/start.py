import os
import subprocess

import click
import mdsynthesis as mds

from .cli import cli
from .util import normalize_host


def get_engine_command(host):
    if host == 'draco':
        return 'sbatch'


@cli.command()
@click.option(
    '--top_folder', help='folder to look for benchmarks', default='.')
@click.option('--host', help='cluster you are running on', default=None)
def start(host, top_folder):
    bundle = mds.discover(top_folder)

    host = normalize_host(host)

    for b in bundle:
        os.chdir(b.abspath)
        subprocess.call([get_engine_command(host), 'bench.job'])
