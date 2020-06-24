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
import numpy as np

from mdbenchmark import console
from mdbenchmark.utils import map_columns, parse_bundle, print_dataframe
from mdbenchmark.versions import VersionFactory


def do_analyze(directory, save_csv):
    """Analyze benchmarks."""
    bundle = dtr.discover(directory)
    version = VersionFactory(categories=bundle.categories).version_class

    df = parse_bundle(
        bundle, columns=version.analyze_categories, sort_values_by=version.analyze_sort,
    )

    # Remove the versions column from the DataFrame
    columns_to_drop = ["version"]
    df = df.drop(columns=columns_to_drop)

    if save_csv is not None:
        if not save_csv.endswith(".csv"):
            save_csv = "{}.csv".format(save_csv)
        df.to_csv(save_csv, index=False)

        console.success("Successfully benchmark data to {}.", save_csv)

    # Reformat NaN values nicely into question marks.
    # move this to the bundle function!
    df = df.replace(np.nan, "?")
    if df.isnull().values.any():
        console.warn(
            "We were not able to gather informations for all systems. "
            "Systems marked with question marks have either crashed or "
            "were not started yet."
        )

    # Warn user that we are going to print more than 50 benchmark results to the console
    if df.shape[0] > 50:
        if click.confirm(
            "We are about to print the results of {} benchmarks to the console. Continue?".format(
                click.style(str(df.shape[0]), bold=True)
            )
        ):
            pass
        else:
            console.error("Exiting.")

    # Print the data to the console
    print_dataframe(
        df, columns=map_columns(version.category_mapping, version.analyze_printing),
    )
