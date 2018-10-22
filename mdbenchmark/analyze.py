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
import mdsynthesis as mds
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from . import console
from .cli import cli
from .mdengines import detect_md_engine, utils
from .plot import plot_over_group
from .utils import generate_output_name, DataFrameFromBundle, PrintDataFrame

plt.switch_backend("agg")


@cli.command()
@click.option(
    "-d",
    "--directory",
    help="Path in which to look for benchmarks.",
    default=".",
    show_default=True,
)
@click.option(
    "-p",
    "--plot",
    is_flag=True,
    help="DEPRECATED. Please use 'mdbenchmark plot'.\nGenerate a plot of finished benchmarks.",
)
@click.option(
    "--ncores",
    "--number-cores",
    "ncores",
    type=int,
    default=None,
    help="Number of cores per node. If not given it will be parsed from the benchmarks' log file.",
    show_default=True,
)
@click.option(
    "-o",
    "--output-name",
    default=None,
    help="Filename for the CSV file containing benchmark results.",
    type=str,
)
def analyze(directory, plot, ncores, output_name):
    """Analyze benchmarks and print the performance results.

    Benchmarks are searched recursively starting from the directory specified
    in `--directory`. If the option is not specified, the working directory
    will be used.

    Benchmarks that have not started yet or finished without printing the
    performance result, will be marked accordingly.

    The benchmark performance results can be saved in a CSV file with the
    `--output-name` option and a custom filename. To plot the results use
    `mdbenchmark plot`.
    """
    bundle = mds.discover(directory)

    df = DataFrameFromBundle(bundle)

    if df.isnull().values.any():
        console.warn(
            "We were not able to gather informations for all systems. "
            "Systems marked with question marks have either crashed or "
            "were not started yet."
        )

    # Reformat NaN values nicely into question marks.
    # move this to the bundle function!
    PrintDataFrame(df)

    # here we determine which output name to use.
    if output_name is None:
        output_name = generate_output_name("csv")
    if ".csv" not in output_name:
        output_name = "{}.csv".format(output_name)
    df.to_csv(output_name)

    if plot:
        console.warn("'--plot' has been deprecated, use '{}'.", "mdbenchmark plot")

        fig = Figure()
        FigureCanvas(fig)
        ax = fig.add_subplot(111)

        df = pd.read_csv(output_name)
        ax = plot_over_group(df, plot_cores=False, ax=ax)
        lgd = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.175))

        fig.tight_layout()
        fig.savefig(
            "runtimes.pdf", type="pdf", bbox_extra_artists=(lgd,), bbox_inches="tight"
        )
