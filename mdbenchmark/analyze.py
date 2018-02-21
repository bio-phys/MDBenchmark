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
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import pandas as pd

from .cli import cli
from .utils import calc_slope_intercept, guess_ncores, lin_func, detect_md_engine, formatted_md_engine_name
import mdengines.gromacs
import mdengines.namd


def plot_analysis(df, ncores):
    # We have to use the matplotlib object-oriented interface directly, because
    # it expects a display to be attached to the system, which we don't on the
    # clusters.
    f = Figure()
    FigureCanvas(f)
    ax = f.add_subplot(111)

    # Remove NaN values. These are missing ncores/performance data.
    df = df.dropna()

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

    gpu_data = df[(df['gpu'])].sort_values('nodes').reset_index()
    if not gpu_data.empty:

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
    if ncores is not None:
        click.echo(
            "Ncores overwritten from CLI. Ignoring values from simulation logs for plot."
        )
        ax2.set_xticklabels(x for x in (axTicks + 1) * ncores)
    else:
        ax2.set_xticklabels(cpu_data['ncores'])

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
    help='Path in which to look for benchmarks.',
    default='.',
    show_default=True)
@click.option(
    '-p',
    '--plot',
    is_flag=True,
    help='Generate a plot of finished benchmarks.')
@click.option(
    '--ncores',
    type=int,
    default=None,
    help='Number of cores per node. If not given it will be parsed from the '
    'benchmarks log file.',
    show_default=True)
@click.option('-e', '--modules', help='MD program files to analyze in directory',
    default='',
    show_default=True,
    multiple=True)
def analyze(directory, plot, ncores, engine):
    """Analyze finished benchmarks."""
    bundle = mds.discover(directory)

    #### TODO TODO TODO
    #### THIS HAS TO BE FIXED!
    ####
    for module in
    engine = formatted_md_engine_name(module)

    df = pd.DataFrame(columns=[
        engine, 'nodes', 'ns/day', 'run time [min]', 'gpu', 'host', 'ncores'
    ])


    for i, sim in enumerate(bundle):
### necessary for mixing modules of different engines in a parent directory
        if 'module' in sim.categories:
                module = sim.categories['module']
        else:
                module = sim.categories['version']

        if engine in module:
            md_engine = detect_md_engine(module)
            df.loc[i] = md_engine.analyze_run(sim)
        else:
            print("skipping a directory")

    if df.isnull().values.any():
        click.echo(
            '{}\tWe were not able to gather informations for all systems.\n\t'
            'Systems marked with question marks have either crashed or\n\t'
            'were not started yet.'.format(
                click.style('WARNING', fg='yellow', bold=True)))

    # Sort values by `nodes`
    df = df.sort_values(['host', engine, 'run time [min]', 'gpu',
                         'nodes']).reset_index(drop=True)

    if df.empty:
        click.echo('{} There is no data for the given path.'.format(
            click.style('ERROR', fg='red', bold=True)))
        sys.exit(1)

    # Reformat NaN values nicely into question marks.
    df_to_print = df.replace(np.nan, '?')
    print(df_to_print)
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
            sys.exit(1)

        # Fail if we have no values at all. This should be some edge case when
        # a user fumbles around with the datreant categories
        if df['gpu'].empty and df[~df['gpu']].empty:
            click.echo('{} There is no data to plot.'.format(
                click.style('ERROR', fg='red', bold=True)))
            sys.exit(1)

        plot_analysis(df, ncores)
