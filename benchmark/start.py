import os
import subprocess

import click
import mdsynthesis as mds

from .cli import cli


def get_engine_command(host):
    if host == 'draco':
        return 'sbatch'


@cli.command()
@click.option('--top_folder', help='folder to look for benchmarks', default='.')
@click.option('--host', help='cluster you are running on')
def start(host, top_folder):
    bundle = mds.discover(top_folder)

    for b in bundle:
        os.chdir(b.abspath)
        subprocess.call([get_engine_command(host), 'bench.job'])
