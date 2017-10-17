import os
import subprocess
from glob import glob

import click
import mdsynthesis as mds

from .cli import cli

PATHS = os.environ['PATH'].split(':')
BATCH_SYSTEMS = {'slurm': 'sbatch', 'sge': 'qsub', 'Loadleveler': 'llsubmit'}


def get_engine_command():
    for p in PATHS:
        for b in BATCH_SYSTEMS.values():
            if glob(os.path.join(p, b)):
                return b
    raise click.UsageError(
        'Was not able to find a batch system. Are you trying to use this '
        'package on a host with a queuing system?')


@cli.command()
@click.option(
    '-d', '--directory', help='directory to search benchmarks in', default='.')
def start(directory):
    """start benchmark simulations found in recursive search of top_folder"""
    bundle = mds.discover(directory)
    for b in bundle:
        os.chdir(b.abspath)
        subprocess.call([get_engine_command(), 'bench.job'])
