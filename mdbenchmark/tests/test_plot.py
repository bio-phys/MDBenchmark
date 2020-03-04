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

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy.testing import assert_equal
from pandas.testing import assert_frame_equal

from mdbenchmark import cli, utils
from mdbenchmark.cli import plot
from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark.testing import data


@pytest.mark.parametrize(
    "size,min_x,plot_cores,xtick_step,xsteps",
    [
        [10, 1, False, None, 1],
        [18, 1, False, None, 2],
        [10, 1, True, None, 1],
        [11, 1, True, None, 3],
        [5, 100, True, None, 3],
        [5, 1, False, 5, 5],
    ],
)
def test_get_xsteps(size, min_x, plot_cores, xtick_step, xsteps):
    """Test the get_xsteps function"""
    assert (
        plot.get_xsteps(
            size=size, min_x=min_x, plot_cores=plot_cores, xtick_step=xtick_step
        )
        == xsteps
    )


def test_plot_gpu(cli_runner, tmpdir, data):
    """Test gpu flage without any host or module.
    """
    with tmpdir.as_cwd():

        output = (
            "Plotting GPU and CPU data.\n"
            "Plotting all hosts in input file.\n"
            "Plotting all modules in your input data.\n"
            "Your file was saved as 'testpng.png' in the working directory.\n"
        )

        result = cli_runner.invoke(
            cli,
            [
                "plot",
                "--csv={}".format(data["test.csv"]),
                "--gpu",
                "--output-name=testpng",
                "--output-format=png",
            ],
        )

        assert result.exit_code == 0
        assert result.output == output
        assert os.path.exists("testpng.png")


@pytest.mark.parametrize("host", ("draco", "hydra"))
def test_plot_host_only(cli_runner, tmpdir, host, data):
    """Test plotting function with one given host.
    """
    with tmpdir.as_cwd():

        output = (
            "Plotting GPU and CPU data.\n"
            "Data for the following hosts will be plotted: {}\n"
            "Plotting all modules in your input data.\n"
            "Your file was saved as 'testpng.png' in the working directory.\n".format(
                host
            )
        )

        result = cli_runner.invoke(
            cli,
            [
                "plot",
                "--csv={}".format(data["test.csv"]),
                "--host={}".format(host),
                "--output-name=testpng",
                "--output-format=png",
            ],
        )

        assert result.exit_code == 0
        assert result.output == output
        assert os.path.exists("testpng.png")


@pytest.mark.parametrize("module", ("gromacs", "namd", "namd/2.12", "gromacs/2018"))
def test_plot_module_only(cli_runner, tmpdir, module, data):
    """Test plotting function with one given engine or module.
    """
    with tmpdir.as_cwd():
        if module in ["gromacs", "namd"]:
            output = (
                "Plotting GPU and CPU data.\n"
                "Plotting all hosts in input file.\n"
                "Plotting all modules for engine '{}'.\n"
                "Your file was saved as 'testpng.png' in the working directory.\n".format(
                    module
                )
            )
        else:
            output = (
                "Plotting GPU and CPU data.\n"
                "Plotting all hosts in input file.\n"
                "Plotting module '{}'.\n"
                "Your file was saved as 'testpng.png' in the working directory.\n".format(
                    module
                )
            )

        result = cli_runner.invoke(
            cli,
            [
                "plot",
                "--csv={}".format(data["test.csv"]),
                "--module={}".format(module),
                "--output-name=testpng",
            ],
        )

        assert result.exit_code == 0
        assert result.output == output
        assert os.path.exists("testpng.png")


@pytest.mark.parametrize("output_type", ("png", "pdf"))
def test_plot_output_type(cli_runner, tmpdir, data, output_type):
    """check whether output types are constructed correctly.
    """
    with tmpdir.as_cwd():

        output = (
            "All modules will be plotted.\n"
            "All hosts will be plotted.\n"
            "A total of 2 runs will be plotted.\n"
            "Your file was saved as 'test.{}' in the working directory.\n".format(
                output_type
            )
        )

        output = (
            "Plotting GPU and CPU data.\n"
            "Plotting all hosts in input file.\n"
            "Plotting all modules in your input data.\n"
            "Your file was saved as 'testfile.{}' in the working "
            "directory.\n".format(output_type)
        )
        result = cli_runner.invoke(
            cli,
            [
                "plot",
                "--csv={}".format(data["test.csv"]),
                "--output-name=testfile",
                "--output-format={}".format(output_type),
            ],
        )
        assert result.output == output
        assert result.exit_code == 0
        # assert os.path.exists("testfile.{}".format(output_type))


@pytest.mark.parametrize("gpu,cpu", [(True, True), (True, False), (False, True)])
def test_plot_filter_dataframe_for_plotting_gpu_and_cpu(
    cli_runner, tmpdir, data, gpu, cpu
):
    """ Checks whether the cpu and gpu filtering works properly.
    """
    with tmpdir.as_cwd():

        input_df = pd.read_csv(data["testcsv.csv"])

        if gpu and not cpu:
            input_df = input_df[input_df.gpu]
        elif not gpu and cpu:
            input_df = input_df[~input_df.gpu]
        elif not gpu and not cpu:
            input_df = pd.read_csv(data["empty_df.csv"])

        real_df = plot.filter_dataframe_for_plotting(
            df=input_df, host_name=(), module_name=(), gpu=gpu, cpu=cpu
        )

        # here we compare the dataframes for any differences
        assert_frame_equal(input_df, real_df)


def test_plot_filter_dataframe_for_plotting_gpu_and_cpu_fail(
    capsys, cli_runner, tmpdir, data
):
    """ Tests the error when gpu and cpu are set to false.
    """
    with tmpdir.as_cwd():
        input_df = pd.read_csv(data["testcsv.csv"])

        expected_output = "ERROR CPU and GPU not set. Nothing to plot. Exiting.\n"
        with pytest.raises(SystemExit) as error:
            plot.filter_dataframe_for_plotting(
                df=input_df, host_name=(), module_name=(), gpu=False, cpu=False
            )
        out, err = capsys.readouterr()
        assert out == expected_output
        assert error.type == SystemExit
        assert error.value.code == 1


@pytest.mark.parametrize(
    "module_name", [("namd/2.12"), ("gromacs/5.1.4-plumed2.3"), ("gromacs"), ("namd")]
)
def test_plot_filter_dataframe_for_plotting_module_name(
    cli_runner, tmpdir, data, module_name
):
    """ Checks whether the module names are filterd correctly in the filtering function.
    """
    with tmpdir.as_cwd():

        expected_df = pd.read_csv(data["testcsv.csv"])
        expected_df = expected_df[expected_df["module"].str.contains(module_name)]

        input_df = pd.read_csv(data["testcsv.csv"])

        module = (module_name,)
        real_df = plot.filter_dataframe_for_plotting(
            df=input_df, host_name=(), module_name=module, gpu=True, cpu=True
        )

        assert_frame_equal(expected_df, real_df)


@pytest.mark.parametrize("host_name", [("hydra"), ("draco")])
def test_plot_filter_dataframe_for_plotting_host_name(
    cli_runner, tmpdir, data, host_name
):
    """ Checks whether the host names are filtered correctly in the filtering function.
    """
    with tmpdir.as_cwd():
        expected_df = pd.read_csv(data["testcsv.csv"])
        expected_df = expected_df[expected_df["host"].str.contains(host_name)]

        input_df = pd.read_csv(data["testcsv.csv"])

        real_df = plot.filter_dataframe_for_plotting(
            df=input_df, host_name=(host_name,), module_name=(), gpu=True, cpu=True
        )

        assert_frame_equal(expected_df, real_df)


def test_plot_filter_empty_dataframe_error(cli_runner, capsys, tmpdir, data):
    """Assert that we exit when given an empty DataFrame through a specific filter combination.
    """
    with tmpdir.as_cwd():
        df = pd.read_csv(data["testcsv.csv"])
        df = df[(~df["gpu"]) & (df["host"] == "draco")]

        with pytest.raises(SystemExit) as error:
            plot.filter_dataframe_for_plotting(
                df=df, host_name=("draco",), module_name=(), gpu=True, cpu=False
            )

        expected_output = (
            "Plotting GPU data only.\n"
            "ERROR Your filtering led to an empty dataset. Exiting.\n"
        )
        out, err = capsys.readouterr()
        assert out == expected_output
        assert error.type == SystemExit
        assert error.value.code == 1


def test_plot_plot_projection(capsys, cli_runner, tmpdir, data):
    """Assert whether the line projection function returns an ax object.
    """
    df = pd.read_csv(data["testcsv.csv"])
    df = df[:2]
    selection = "nodes"
    color = "grey"
    fig = Figure()
    FigureCanvas(fig)
    ax = fig.add_subplot(111)
    plot.plot_projection(df=df, selection=selection, color=color, ax=ax)


def test_plot_plot_line(capsys, cli_runner, tmpdir, data):
    """Assert whether the single plot entry works and returns an ax object.
    """
    df = pd.read_csv(data["testcsv.csv"])
    df = df[:2]
    selection = "nodes"
    label = "test"
    fig = Figure()
    FigureCanvas(fig)
    ax = fig.add_subplot(111)
    plot.plot_line(df=df, selection=selection, label=label, fit=True, ax=ax)


def test_plot_plot_line_singlepoint(capsys, cli_runner, tmpdir, data):
    """Assert whether the single plot entry works and returns an ax object.
    """
    df = pd.read_csv(data["testcsv.csv"])
    df = df[:1]
    selection = "nodes"
    label = "test"
    fig = Figure()
    FigureCanvas(fig)
    ax = fig.add_subplot(111)
    plot.plot_line(df=df, selection=selection, label=label, fit=True, ax=ax)
