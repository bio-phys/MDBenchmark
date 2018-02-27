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
from .utils import calc_slope_intercept, lin_func


def plot_line(df, label, ax=None):
    if ax is None:
        ax = plt.gca()

    p = ax.plot('nodes', 'ns/day', '.-', data=df, ms='10', label=label)
    color = p[0].get_color()
    slope, intercept = calc_slope_intercept(
        (df['nodes'].iloc[0], df['ns/day'].iloc[0]), (df['nodes'].iloc[1],
                                                      df['ns/day'].iloc[1]))
    # avoid a label and use values instead of pd.Series
    ax.plot(
        df['nodes'],
        lin_func(df['nodes'].values, slope, intercept),
        ls='--',
        color=color,
        alpha=.5)
    return ax


def plot_over_group(df, groupby, ax=None):
    # plot all lines
    gb = df.groupby(groupby)
    for key, df in gb:
        label = ' '.join(['{}={}'.format(n, v) for n, v in zip(groupby, key)])
        plot_line(ax=ax, df=df, label=label)

    # style axes
    ax.set_xlabel('Number of nodes')
    ax.set_ylabel('Performance [ns/day]')
    ax.legend()

    ax2 = ax.twiny()
    ax1_xticks = ax.get_xticks()
    ax2.set_xticks(ax1_xticks)
    ax2.set_xbound(ax.get_xbound())
    ax2.set_xticklabels(gb.get_group(list(gb.groups.keys())[0])['ncores'])
    ax2.set_xlabel('{}'.format('{}\n\nCores'.format(df['host'][0])))

    return ax


@cli.command()
@click.option('--csv', help='name of csv file')
@click.option(
    '--groupby',
    '-g',
    type=str,
    help='columns to groupby for plot as comma separated string',
    default='gpu, module',
    show_default=True)
def plot(csv, groupby):
    """Plot nice things"""
    df = pd.read_csv(csv, index_col=0)
    # Remove NaN values. These are missing ncores/performance data.
    df = df.dropna()
    # We have to use the matplotlib object-oriented interface directly, because
    # it expects a display to be attached to the system, which we don't on the
    # clusters.
    fig = Figure()
    FigureCanvas(fig)
    ax = fig.add_subplot(111)
    # remove whitespace
    groupby = [s.strip() for s in groupby.split(',')]
    plot_over_group(df, groupby, ax=ax)
    fig.savefig('results.pdf')
