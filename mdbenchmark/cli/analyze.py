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
import datreant as dtr
import numpy as np

from mdbenchmark import console
from mdbenchmark.utils import DataFrameFromBundle, PrintDataFrame


def do_analyze(directory, save_csv):
    """Analyze benchmarks."""
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
