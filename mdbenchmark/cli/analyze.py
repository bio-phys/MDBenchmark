# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017-2019 The MDBenchmark development team and contributors
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

from mdbenchmark import console
from mdbenchmark.cli.plot import plot_over_group
from mdbenchmark.mdengines import detect_md_engine, utils
from mdbenchmark.migrations import mds_to_dtr
from mdbenchmark.utils import DataFrameFromBundle, PrintDataFrame, generate_output_name

plt.switch_backend("agg")


def do_analyze(directory, plot, ncores, save_csv):
    """Analyze benchmarks."""
    # Migrate from MDBenchmark<2 to MDBenchmark=>2
    mds_to_dtr.migrate_to_datreant(directory)

    bundle = dtr.discover(directory)

    df = DataFrameFromBundle(bundle)

    if save_csv is not None and not save_csv.endswith(".csv"):
        save_csv = "{}.csv".format(save_csv)
    df.to_csv(save_csv)

    # Reformat NaN values nicely into question marks.
    # move this to the bundle function!
    df = df.replace(np.nan, "?")
    if df.isnull().values.any():
        console.warn(
            "We were not able to gather informations for all systems. "
            "Systems marked with question marks have either crashed or "
            "were not started yet."
        )
    PrintDataFrame(df)

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
