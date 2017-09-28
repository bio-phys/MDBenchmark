import os
import subprocess
from glob import glob

import click
import mdsynthesis as mds

from .cli import cli

PATHS = os.environ['PATH'].split(':')
BATCH_SYSTEMS = {'slurm': 'sbatch',
                 'sge': 'qsub',
                 'Loadleveler': 'llsubmit'}


def get_engine_command():
    for p in PATHS:
        for b in BATCH_SYSTEMS.values():
            if glob(os.path.join(p, b)):
                return b
    raise RuntimeError("Didn't find a batch system")


@cli.command()
@click.option(
    '--top_folder', help='folder to look for benchmarks', default='.')
def start(top_folder):
    """start benchmark simulations found in recursive search of top_folder"""
    bundle = mds.discover(top_folder)
    for b in bundle:
        os.chdir(b.abspath)
        subprocess.call([get_engine_command(), 'bench.job'])
