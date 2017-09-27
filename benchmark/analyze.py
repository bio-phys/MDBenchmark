import os
import socket
from glob import glob

import click
import mdsynthesis as mds
import numpy as np
import pandas as pd

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from .cli import cli


def analyze_run(sim):
    ns_day = 0

    output_files = glob(os.path.join(sim.relpath, '*log*'))
    if output_files:
        with open(output_files[0]) as fh:
            err = fh.readlines()
        for line in err:
            if 'Performance' in line:
                ns_day = float(line.split()[1])
                break

    return (sim.categories['version'], sim.categories['nodes'], ns_day,
            sim.categories['gpu'], socket.gethostname())


def plot(df):
    gb = df.groupby('gpu')
    fig, ax = plt.subplots()

    gpu = gb.get_group(True)
    # adopt names for seaborn legend
    gpu['gromacs'] = gpu['gromacs'].apply(lambda e: '{}-gpu'.format(e))

    sns.tsplot(
        gpu,
        time='nodes',
        value='ns/day',
        condition='gromacs',
        unit='host',
        ax=ax,
        color=sns.color_palette('hls', 3),
        marker='o')
    sns.tsplot(
        gb.get_group(False),
        time='nodes',
        value='ns/day',
        condition='gromacs',
        unit='host',
        ax=ax,
        marker='o')

    max_nodes = df['nodes'].max()
    min_nodes = df['nodes'].min()

    ax.set(
        xlim=(min_nodes - .5, max_nodes + .5),
        xticks=np.arange(min_nodes, max_nodes + 1),
        title=socket.gethostname())

    fig.savefig('runtimes.pdf')


@cli.command()
@click.option('--top_folder', help='folder to look for benchmarks')
@click.option('--plot', is_flag=True, help='plot performance')
def analyze(top_folder, plot):
    bundle = mds.discover(top_folder)
    df = pd.DataFrame(columns=['gromacs', 'nodes', 'ns/day', 'gpu', 'host'])
    for i, sim in enumerate(bundle):
        df.loc[i] = analyze(sim)
    print(df)
    df.to_csv('runtimes.csv')
    if plot:
        plot(df)
