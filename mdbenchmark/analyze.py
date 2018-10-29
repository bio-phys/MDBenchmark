# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017-2018 The MDBenchmark development team and contributors
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

import datreant as dtr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from . import console
from .cli import cli
from .mdengines import detect_md_engine, utils
from .migrations import mds_to_dtr
from .plot import plot_over_group
from .utils import DataFrameFromBundle, PrintDataFrame, generate_output_name

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
    help="DEPRECATED. Please use 'mdbenchmark plot'.\nNumber of cores per node. If not given it will be parsed from the benchmarks' log file.",
    show_default=True,
)
@click.option(
    "-s",
    "--save-csv",
    default=None,
    help="Filename for the CSV file containing benchmark results.",
)
def analyze(directory, plot, ncores, save_csv):
    """Analyze benchmarks and print the performance results.

    Benchmarks are searched recursively starting from the directory specified
    in ``--directory``. If the option is not specified, the working directory
    will be used.

    Benchmarks that have not started yet or finished without printing the
    performance result, will be marked accordingly.

    The benchmark performance results can be saved in a CSV file with the
    ``--save-csv`` option and a custom filename. To plot the results use
    ``mdbenchmark plot``.
    """

    # Migrate from MDBenchmark<2 to MDBenchmark=>2
    mds_to_dtr.migrate_to_datreant(directory)

    bundle = dtr.discover(directory)

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

    if save_csv is not None and not save_csv.endswith(".csv"):
        save_csv = "{}.csv".format(save_csv)
    df.to_csv(save_csv)

    if plot:
        console.warn("'--plot' has been deprecated, use '{}'.", "mdbenchmark plot")

        fig = Figure()
        FigureCanvas(fig)
        ax = fig.add_subplot(111)

        df = pd.read_csv(save_csv)
        if ncores:
            console.warn(
                "Ignoring your value from '{}' and parsing number of cores from log files.",
                "--number-cores/-ncores",
            )
        ax = plot_over_group(df, plot_cores=ncores, fit=True, ax=ax)
        lgd = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.175))

        fig.tight_layout()
        fig.savefig(
            "runtimes.pdf", type="pdf", bbox_extra_artists=(lgd,), bbox_inches="tight"
        )
