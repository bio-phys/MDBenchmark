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
import os

import datreant as dtr
import numpy as np
import pandas as pd

from mdbenchmark import cli
from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark.testing import data, datafiles
from mdbenchmark.utils import ConsolidateDataFrame, DataFrameFromBundle, PrintDataFrame


def test_analyze_gromacs(cli_runner, tmpdir, data):
    """Test that the output is OK when all outputs are fine."""
    with tmpdir.as_cwd():

        result = cli_runner.invoke(
            cli, ["analyze", "--directory={}".format(data["analyze-files-gromacs"])]
        )

        df = pd.read_csv(data["analyze-files-gromacs.csv"])
        test_output = PrintDataFrame(df, False) + "\n"
        assert result.exit_code == 0
        assert result.output == test_output


def test_analyze_namd(cli_runner, tmpdir, data):
    with tmpdir.as_cwd():
        result = cli_runner.invoke(
            cli, ["analyze", "--directory={}".format(data["analyze-files-namd"])]
        )

        bundle = dtr.discover(data["analyze-files-namd"])
        df = DataFrameFromBundle(bundle)
        test_output = PrintDataFrame(df, False) + "\n"

        assert result.exit_code == 0
        assert result.output == test_output


def test_analyze_with_errors(cli_runner, tmpdir, data):
    """Test that we warn the user of errors in the output files. Also test that we
show a question mark instead of a float in the corresponding cell.
    """
    with tmpdir.as_cwd():

        result = cli_runner.invoke(
            cli, ["analyze", "--directory={}".format(data["analyze-files-w-errors"])]
        )

        bundle = dtr.discover(data["analyze-files-w-errors"])
        df = DataFrameFromBundle(bundle)
        df = df.replace(np.nan, "?")
        test_output = PrintDataFrame(df, False) + "\n"

        assert result.exit_code == 0
        assert result.output == test_output


def test_analyze_plot(cli_runner, tmpdir, data):
    with tmpdir.as_cwd():

        result = cli_runner.invoke(
            cli,
            [
                "analyze",
                "--directory={}".format(data["analyze-files-gromacs"], "--plot"),
            ],
        )

        bundle = dtr.discover(data["analyze-files-gromacs"])
        df = DataFrameFromBundle(bundle)
        test_output = PrintDataFrame(df, False) + "\n"

        assert result.exit_code == 0
        assert result.output == test_output
        os.path.isfile("runtimes.pdf")


def test_analyze_console_messages(cli_runner, tmpdir):
    """Test that the CLI for analyze prints all error messages as expected."""
    with tmpdir.as_cwd():
        # Test error message if the TPR file does not exist
        result = cli_runner.invoke(cli, ["analyze", "--directory=look_here/"])
        output = "ERROR There is no data for the given path.\n"
        assert result.exit_code == 1
        assert result.output == output
