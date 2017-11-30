# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017 Max Linke & Michael Gecht and contributors
# (see the file AUTHORS for the full list of names)
#
# MDBenchmark is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MDBenchmark is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MDBenchmark.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys
from glob import glob

import click
import mdsynthesis as mds
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from .cli import cli
from .utils import calc_slope_intercept, guess_ncores, lin_func


def analyze_run(sim):
    ns_day = 0

    # search all output files and ignore GROMACS backup files
    output_files = glob(os.path.join(sim.relpath, '[!#]*log*'))
    if output_files:
        with open(output_files[0]) as fh:
            err = fh.readlines()
        for line in err:
            if 'Performance' in line:
                ns_day = float(line.split()[1])
                break

    # Backward compatibility to previously created mdbenchmark systems
    if 'time' not in sim.categories:
        sim.categories['time'] = 0

    # backward compatibility
    if 'module' in sim.categories:
        module = sim.categories['module']
    else:
        module = sim.categories['version']

    return (module, sim.categories['nodes'], ns_day, sim.categories['time'],
            sim.categories['gpu'], sim.categories['host'])


def plot_analysis(df, ncores):
    # We have to use the matplotlib object-oriented interface directly, because
    # it expects a display to be attached to the system, which we don't on the
    # clusters.
    f = Figure()
    FigureCanvas(f)
    ax = f.add_subplot(111)

    max_x = df['nodes'].max()
    max_y = df['ns/day'].max()
    if not max_y:
        max_y = 50

    y_tick_steps = 10
    if max_y > 100:
        y_tick_steps = 20

    x = np.arange(1, max_x + 1, 1)

    if not df[~df['gpu']].empty:
        cpu_data = df[(~df['gpu'])].sort_values('nodes').reset_index()
        ax.plot(cpu_data['ns/day'], '.-', ms='10', color='C0', label='CPU')
        slope, intercept = calc_slope_intercept(x[0], cpu_data['ns/day'][0],
                                                x[1], cpu_data['ns/day'][1])
        ax.plot(
            x - 1,
            lin_func(x, slope, intercept),
            ls='dashed',
            color='C0',
            alpha=0.5)

    if not df['gpu'].empty:
        gpu_data = df[(df['gpu'])].sort_values('nodes').reset_index()

        ax.plot(gpu_data['ns/day'], '.-', ms='10', color='C1', label='GPU')
        slope, intercept = calc_slope_intercept(x[0], gpu_data['ns/day'][0],
                                                x[1], gpu_data['ns/day'][1])
        ax.plot(
            x - 1,
            lin_func(x, slope, intercept),
            ls='dashed',
            color='C1',
            alpha=0.5)

    ax.set_xticks(x - 1)
    ax.set_xticklabels(x)

    axTicks = ax.get_xticks()

    ax2 = ax.twiny()
    ax2.set_xticks(axTicks)
    ax2.set_xbound(ax.get_xbound())
    ax2.set_xticklabels(x for x in (axTicks + 1) * ncores)

    ax.set_xlabel('Number of nodes')
    ax.set_ylabel('Performance [ns/day]')

    ax.set_yticks(np.arange(0, (max_y + (max_y * 0.5)), y_tick_steps))
    ax.set_ylim(ymin=0, ymax=(max_y + (max_y * 0.2)))

    ax2.set_xlabel('{}'.format('{}\n\nCores'.format(df['host'][0])))

    ax.legend()

    f.tight_layout()
    f.savefig('runtimes.pdf', format='pdf')


@cli.command()
@click.option(
    '-d',
    '--directory',
    help='directory to search benchmarks in',
    default='.',
    show_default=True)
@click.option('-p', '--plot', is_flag=True, help='create plot of mdbenchmarks')
@click.option(
    '--ncores',
    type=int,
    default=guess_ncores(),
    help='Number of cores per node. If not given we try to guess this number '
    'based on the current host',
    show_default=True)
def analyze(directory, plot, ncores):
    """analyze finished benchmark."""
    bundle = mds.discover(directory)
    df = pd.DataFrame(columns=[
        'gromacs', 'nodes', 'ns/day', 'run time [min]', 'gpu', 'host'
    ])

    for i, sim in enumerate(bundle):
        df.loc[i] = analyze_run(sim)

    # Sort values by `nodes`
    df = df.sort_values(['host', 'gromacs', 'run time [min]', 'gpu',
                         'nodes']).reset_index(drop=True)
    print(df)
    df.to_csv('runtimes.csv')

    if plot:
        df = pd.read_csv('runtimes.csv')

        # We only support plotting of mdbenchmark systems from equal hosts /
        # with equal settings
        uniqueness = df.apply(lambda x: x.nunique())
        if uniqueness['gromacs'] > 1 or uniqueness['host'] > 1:
            click.echo(
                '{} Cannot plot benchmarks for more than one GROMACS module'
                ' and/or host.'.format(
                    click.style('ERROR', fg='red', bold=True)))
            sys.exit(0)

        # Fail if we have no values at all. This should be some edge case when
        # a user fumbles around with the datreant categories
        if df['gpu'].empty and df[~df['gpu']].empty:
            click.echo('There is no data to plot.')
            sys.exit(0)

        plot_analysis(df, ncores)
