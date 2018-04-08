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
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import click

from .cli import cli
from .utils import calc_slope_intercept, lin_func, generate_output_name
from . import console


def plot_line(df, df_sel, label, ax=None):
    if ax is None:
        ax = plt.gca()

    p = ax.plot(df_sel, 'ns/day', '.-', data=df, ms='10', label=label)
    color = p[0].get_color()
    slope, intercept = calc_slope_intercept(
        (df[df_sel].iloc[0], df['ns/day'].iloc[0]), (df[df_sel].iloc[1],
                                                     df['ns/day'].iloc[1]))
    # avoid a label and use values instead of pd.Series
    ax.plot(
        df[df_sel],
        lin_func(df[df_sel].values, slope, intercept),
        ls='--',
        color=color,
        alpha=.5)
    return ax


def plot_over_group(df, plot_cores, ax=None):
    # plot all lines
    df_sel = 'ncores' if plot_cores else 'nodes'

    gb = df.groupby(['gpu', 'module', 'host'])
    groupby = ['gpu', 'module', 'host']
    for key, df in gb:
        label = ' '.join(['{}={}'.format(n, v) for n, v in zip(groupby, key)])
        plot_line(df=df, df_sel=df_sel, ax=ax, label=label)

    # style axes
    xlabel = 'cores' if plot_cores else 'nodes'
    ax.set_xlabel('Number of {}'.format(xlabel))
    ax.set_ylabel('Performance [ns/day]')
    ax.legend()

    return ax


def filter_dataframe_for_plotting(df, host_name, module_name, gpu, cpu):
    # gpu/cpu can be plotted together or separately
    if gpu and cpu:
        # if no flags are given by the user or both are set everything is plotted
        console.info("plotting GPU and CPU data.")
    elif gpu and not cpu:
        df = df[df.gpu]
        console.info("plotting GPU data only.")
    elif cpu and not gpu:
        df = df[~df.gpu]
        console.info("plotting CPU data only.")
    elif not cpu and not gpu:
        console.error("CPU and GPU not set. Nothing to plot. Exiting")

    for host in host_name:
        if host in df['host'].tolist():
            df = df[df['host'].isin(host_name)]
            console.info('Data for the following hosts will be plotted: {}.', set(host_name))
        elif not host:
            # dataframe stays the same and all hosts will be plotted
            console.info('All hosts will be plotted.')
        elif host not in df['host'].tolist():
            # filter host names that don't exist
            console.error('The host {} does not exist in your csv data. Exiting.', host)

    if not host_name:
        console.info("plotting all hosts in csv.")

    for module in module_name:
        if module in ['gromacs', 'namd']:
            console.info("plotting all modules for engine {}.", module)
        elif module not in df['module'].tolist():
            console.error("The module {} does not exist in your data. Exiting.", module)

    if not module_name:
        console.info("plotting all modules in your input data.")
    # this should work but we need to check before whether any of the entered
    # names are faulty/don't exist
    if module_name:
        df = df[df['module'].str.contains('|'.join(module_name))]

    if df.empty:
        console.error(
            'Your selections contained no Benchmarking Information.\n'
            'Are you sure all your selections are correct?')

    return df


@cli.command()
@click.option(
    '--csv',
    help='Name of csv file to plot.',
    multiple=True)
@click.option(
    '--output-name',
    '-o',
    help="Name of output file.")
@click.option(
    '--output-type',
    '-t',
    help="File extension for output file.",
    type=click.Choice(['png', 'pdf', 'svg', 'ps']),
    show_default=True,
    default='png')
@click.option(
    '--module-name',
    '-h',
    multiple=True,
    help="Module name or engine name (gromacs, namd) which is plotted.")
@click.option(
    '--host-name',
    '-h',
    multiple=True,
    help="Host name which is plotted.")
@click.option(
    '--gpu/--no-gpu',
    help="Plot data for GPU runs.",
    show_default=True,
    default=True)
@click.option(
    '--cpu/--no-cpu',
    help="Plot data for CPU runs.",
    show_default=True,
    default=True)
@click.option(
    '--plot-cores',
    help="Plot performance per core instead of nodes",
    show_default=True,
    is_flag=True)
def plot(csv, output_name, output_type, host_name, module_name, gpu, cpu, plot_cores):
    """Generate plots from csv files"""
    print(host_name)
    if not csv:
        console.error("No csv file specified. use --csv to specify a file.")

    df = pd.concat([pd.read_csv(c, index_col=0) for c in csv]).dropna()

    df = filter_dataframe_for_plotting(df, host_name, module_name, gpu, cpu)

    fig = Figure()
    FigureCanvas(fig)
    ax = fig.add_subplot(111)
    plot_over_group(df, plot_cores, ax=ax)

    if output_name is None:
        output_name = generate_output_name(output_type)
    elif output_name.endswith('.{}'.format(output_type)):
        output_name = '{}.{}'.format(output_name, output_type)
    fig.savefig(output_name, type=output_type)
    console.info(
        'Your file was saved as {} in the working directory.', output_name)
