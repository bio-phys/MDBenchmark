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

from . import console
from .cli import cli
from .mdengines import detect_md_engine, utils
from .utils import (calc_slope_intercept, generate_output_name, guess_ncores,
                    lin_func)


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
        console.info(
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
@click.option(
    '-o',
    '--output-name',
    default=None,
    help="Name of the output .csv file.",
    type=str)
def analyze(directory, plot, ncores, output_name):
    """Analyze finished benchmarks."""
    bundle = mds.discover(directory)

    df = pd.DataFrame(columns=[
        'module', 'nodes', 'ns/day', 'run time [min]', 'gpu', 'host', 'ncores'
    ])

    for i, sim in enumerate(bundle):
        # older versions wrote a version category. This ensures backwards compatibility
        if 'module' in sim.categories:
            module = sim.categories['module']
        else:
            module = sim.categories['version']
        # call the engine specific analysis functions
        engine = detect_md_engine(module)
        df.loc[i] = utils.analyze_run(engine=engine, sim=sim)

    if df.empty:
        console.error('There is no data for the given path.')

    if df.isnull().values.any():
        console.warn(
            'We were not able to gather informations for all systems. '
            'Systems marked with question marks have either crashed or '
            'were not started yet.')

    # Sort values by `nodes`
    df = df.sort_values(['host', 'module', 'run time [min]', 'gpu',
                         'nodes']).reset_index(drop=True)

    # Reformat NaN values nicely into question marks.
    df_to_print = df.replace(np.nan, '?')
    with pd.option_context('display.max_rows', None):
        print(df_to_print)

    # here we determine which output name to use.
    if output_name is None:
        output_name = generate_output_name("csv")
    if '.csv' not in output_name:
        output_name = '{}.csv'.format(output_name)
    df.to_csv(output_name)

    if plot:
        df = pd.read_csv(output_name)

        # We only support plotting of benchmark systems from equal hosts /
        # with equal settings
        uniqueness = df.apply(lambda x: x.nunique())

        # Backwards compatibility to older versions.
        if 'module' in uniqueness:
            module_column = uniqueness['module']
        else:
            module_column = uniqueness['gromacs']

        if module_column > 1 or uniqueness['host'] > 1:
            console.error(
                'Cannot plot benchmarks for more than one GROMACS module '
                'and/or host.')

        # Fail if we have no values at all. This should be some edge case when
        # a user fumbles around with the datreant categories
        if df['gpu'].empty and df[~df['gpu']].empty:
            console.error('There is no data to plot.')

        plot_analysis(df, ncores)
