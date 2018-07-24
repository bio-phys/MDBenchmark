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
import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from . import console
from .cli import cli
from .utils import calc_slope_intercept, generate_output_name, lin_func

plt.switch_backend('agg')


def plot_line(df, selection, label, ax=None):
    if ax is None:
        ax = plt.gca()

    p = ax.plot(selection, 'ns/day', '.-', data=df, ms='10', label=label)
    color = p[0].get_color()
    slope, intercept = calc_slope_intercept(
        (df[selection].iloc[0], df['ns/day'].iloc[0]),
        (df[selection].iloc[1], df['ns/day'].iloc[1]))
    # avoid a label and use values instead of pd.Series
    ax.plot(
        df[selection],
        lin_func(df[selection].values, slope, intercept),
        ls='--',
        color=color,
        alpha=.5)
    return ax


def plot_over_group(df, plot_cores, ax=None):
    # plot all lines
    selection = 'ncores' if plot_cores else 'nodes'

    groupby = ['gpu', 'module', 'host']
    gb = df.groupby(groupby)
    for key, df in gb:
        label = ' '.join(['{}={}'.format(n, v) for n, v in zip(groupby, key)])
        plot_line(df=df, selection=selection, ax=ax, label=label)

    # style axes
    xlabel = 'cores' if plot_cores else 'nodes'
    ax.set_xlabel('Number of {}'.format(xlabel))
    ax.set_ylabel('Performance [ns/day]')

    # here I return the figure as well as the legend
    return ax


def filter_dataframe_for_plotting(df, host_name, module_name, gpu, cpu):
    # gpu/cpu can be plotted together or separately
    if gpu and cpu:
        # if no flags are given by the user or both are set everything is plotted
        console.info("Plotting GPU and CPU data.")
    elif gpu and not cpu:
        df = df[df.gpu]
        console.info("Plotting GPU data only.")
    elif cpu and not gpu:
        df = df[~df.gpu]
        console.info("Plotting CPU data only.")
    elif not cpu and not gpu:
        console.error("CPU and GPU not set. Nothing to plot. Exiting.")

    if df.empty:
        console.error("Your filtering led to an empty dataset. Exiting.")

    df_filtered_hosts = df[df['host'].isin(host_name)]
    df_unique_hosts = np.unique(df_filtered_hosts['host'])

    if df_unique_hosts.size != len(host_name):
        console.error("Could not find all provided hosts. Available hosts are: {}".format(
            ', '.join(np.unique(df['host']))))

    if not host_name:
        console.info("Plotting all hosts in csv.")
    else:
        df = df_filtered_hosts
        console.info("Data for the following hosts will be plotted: {}".format(
            ', '.join(df_unique_hosts)))

    for module in module_name:
        if module in ['gromacs', 'namd']:
            console.info("Plotting all modules for engine {}.", module)
        elif module in df['module'].tolist():
            console.info("Plotting module {}.", module)
        elif module not in df['module'].tolist():
            console.error("The module {} does not exist in your data. Exiting.", module)

    if not module_name:
        console.info("Plotting all modules in your input data.")
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
    help="Plot performance per core instead of nodes.",
    show_default=True,
    is_flag=True)
def plot(csv, output_name, output_type, host_name, module_name, gpu, cpu, plot_cores):
    """Generate plots from csv files"""

    if not csv:
        raise click.BadParameter('You must specify at least one csv file.', param_hint='"--csv"')

    df = pd.concat([pd.read_csv(c, index_col=0) for c in csv]).dropna()

    df = filter_dataframe_for_plotting(df, host_name, module_name, gpu, cpu)

    fig = Figure()
    FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax = plot_over_group(df, plot_cores, ax=ax)
    lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.175))
    plt.tight_layout()

    if output_name is None and len(csv) == 1:
        csv_string = csv[0].split(".")[0]
        output_name = '{}.{}'.format(csv_string, output_type)
    elif output_name is None and len(csv) != 1:
        output_name = generate_output_name(output_type)
    elif not output_name.endswith('.{}'.format(output_type)):
        output_name = '{}.{}'.format(output_name, output_type)
    # tight alone does not consider the legend if it is outside the plot.
    # therefore i add it manually as extra artist. This way we don't get problems
    # with the variability of individual lines which are to be plotted
    fig.savefig(output_name, type=output_type, bbox_extra_artists=(lgd,), bbox_inches='tight')
    console.info(
        'Your file was saved as {} in the working directory.', output_name)
