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
import numpy as np
import pytest
import os
import pandas as pd
from numpy.testing import assert_equal
from pandas.testing import assert_frame_equal

from mdbenchmark import utils
from mdbenchmark import cli
from mdbenchmark import plot
from mdbenchmark.testing import data
from mdbenchmark.ext.click_test import cli_runner


# @pytest.mark.parametrize('module_selection', 'host', [
#     ('gromacs/2018', 'draco'),
#     ('namd/2.12', 'draco'),
#     ('gromacs/2016.3', 'hydra')
# ])
# def test_plot_filtering_success(cli_runner, tmpdir, data module_selection, expected_df, host):
#     """Test whether we can plot over different groups.
#     """
#     with tmpdir.as_cwd():
#
#         output = 'The following modules will be plotted {{'{}'}}.\n'.format{module_selection} \
#                  'Your file was saved as testpng.png in the working directory.''
#
#         result = cli_runner.invoke(cli.cli, [
#             'plot',
#             '--csv=test.csv', '--module-name={}'.format(module_selection),
#             '--host-name={}'.format(host), '--output-name=testpng'
#         ])
#         assert result.exit_code == 0
#         assert result.output == output
#         assert os.path.exists("testpng.png")

# @pytest.mark.parametrize('module_selection', 'host', [
#     ('gromacs/2018', 'failengine'),
#     ('failengine', 'draco')
# ])
# def test_plot_filtering_fail(cli_runner, tmpdir, data, module_selection, host):
#     """Test unsuccessful filtering and error message.
#     """
#     with tmpdir.as_cwd():
#
#         output = ''
#
#         result = cli_runner.invoke(cli.cli, [
#             'plot',
#             '--csv={}'.format(data['test.csv']), '--module-name={}'.format(module_selection),
#             '--host-name={}'.format(host), '--output-name=testpng'
#         ])
#
#         assert result.output == output
#         assert result.exit_code == 1


def test_plot_gpu(cli_runner, tmpdir, data):
    """Test gpu flage without any host or module.
    """
    with tmpdir.as_cwd():
        output = 'All modules will be plotted.\n' \
                 'All hosts will be plotted.\n' \
                 'A total of 4 runs will be plotted.\n' \
                 'Your file was saved as testpng.png in the working directory.\n' \

        result = cli_runner.invoke(cli.cli, [
            'plot',
            '--csv={}'.format(data['test.csv']), '--gpu', '--output-name=testpng.png'
        ])

        assert result.exit_code == 0
        assert result.output == output
        assert os.path.exists("testpng.png")


@pytest.mark.parametrize('host', ('draco', 'hydra'))
def test_plot_host_only(cli_runner, tmpdir, host, data):
    """Test only giving a host.
    """
    with tmpdir.as_cwd():

        output = 'All modules will be plotted.\n' \
                 'Data for the following hosts will be plotted: {{\'{}\'}}.\n'\
                 'A total of 1 runs will be plotted.\n' \
                 'Your file was saved as testpng.png in the working directory.\n'.format(host)

        result = cli_runner.invoke(cli.cli, [
            'plot',
            '--csv={}'.format(data['test.csv']), '--host-name={}'.format(host),
            '--output-name=testpng.png'
        ])

        assert result.exit_code == 0
        assert result.output == output
        assert os.path.exists("testpng.png")


# @pytest.mark.parametrize('module', ('gromacs', 'namd', 'namd/2.12', 'gromacs/2018'))
# def test_plot_module_only(cli_runner, tmpdir, module):
#     """Test only giving a module.
#     """
#     with tmpdir.as_cwd():
#
#         output = ''
#
#         result = cli_runner.invoke(cli.cli, [
#             'plot',
#             '--csv=test.csv', '--module-name={}'.format(module_selection),
#             '--host-name={}'.format(host), '--output-name=testpng'
#         ])
#
#
@pytest.mark.parametrize('output_type', ('png', 'pdf'))
def test_plot_output_type(cli_runner, tmpdir, data, output_type):
    """check whether output types are constructed correctly
    """
    with tmpdir.as_cwd():

        output = 'All modules will be plotted.\n' \
                 'All hosts will be plotted.\n' \
                 'A total of 2 runs will be plotted.\n' \
                 'Your file was saved as test.{} in the working directory.\n'.format(output_type)

        result = cli_runner.invoke(cli.cli, [
            'plot',
            '--csv={}'.format(data['test.csv']), '--output-name=testfile', '--output-type={}'.format(output_type)
        ])
        assert result.exit_code == 0
        assert os.path.exists("testfile.{}".format(output_type))


@pytest.mark.parametrize("gpu,cpu", [
    (True, True),
    (True, False),
    (False, True),
])
def test_plot_filter_dataframe_for_plotting_gpu_and_cpu(cli_runner, tmpdir, data, gpu, cpu):
    """ check whether output types are constructed correctly
    """
    with tmpdir.as_cwd():

        input_df = pd.read_csv(data['testcsv.csv'])

        test_df = input_df

        if gpu and not cpu:
            input_df = input_df[input_df.gpu]
        elif not gpu and cpu:
            input_df = input_df[~input_df.gpu]
        elif not gpu and not cpu:
            input_df = pd.read_csv(data['empty_df.csv'])

        real_df = plot.filter_dataframe_for_plotting(df=input_df, host_name=(), module_name=(), gpu=gpu, cpu=cpu)

        # here we compare the dataframes for any differences
        assert_frame_equal(input_df, real_df)


@pytest.mark.parametrize("gpu,cpu", [
    (False, False)
])
def test_plot_filter_dataframe_for_plotting_gpu_and_cpu_fail(capsys, cli_runner, tmpdir, data, gpu, cpu):
    """ check whether output types are constructed correctly
    """
    with tmpdir.as_cwd():
        input_df = pd.read_csv(data['testcsv.csv'])

        expected_output = "CPU and GPU not set. Nothing to plot. Exiting."
        plot.filter_dataframe_for_plotting(df=input_df, host_name=(), module_name=(), gpu=gpu, cpu=cpu)
        out, err = capsys.readouterr()
        assert out == expected_output

@pytest.mark.parametrize('module_name', [
    ('namd/2.12'),
    ('gromacs/5.1.4-plumed2.3'),
    ('gromacs'),
    ('namd')
])
def test_plot_filter_dataframe_for_plotting_module_name(cli_runner, tmpdir, data, module_name):
    """ check whether output types are constructed correctly
    """
    with tmpdir.as_cwd():

        expected_df = pd.read_csv(data['testcsv.csv'])
        expected_df = expected_df[expected_df['module'].str.contains(module_name)]

        input_df = pd.read_csv(data['testcsv.csv'])

        module = (module_name,)
        real_df = plot.filter_dataframe_for_plotting(df=input_df, host_name=(), module_name=module, gpu=True, cpu=True)

        assert_frame_equal(expected_df, real_df)


@pytest.mark.parametrize("host_name", [
    ('hydra'),
    ('draco')
])
def test_plot_filter_dataframe_for_plotting_host_name(cli_runner, tmpdir, data, host_name):
    """ check whether output types are constructed correctly
    """
    with tmpdir.as_cwd():

        expected_df = pd.read_csv(data['testcsv.csv'])
        expected_df = expected_df[expected_df['host'].str.contains(host_name)]

        input_df = pd.read_csv(data['testcsv.csv'])

        # I have to convert the variable to a tuple, otherwise this appears not to work
        host = (host_name,)
        real_df = plot.filter_dataframe_for_plotting(df=input_df, host_name=host, module_name=(), gpu=True, cpu=True)

        assert_frame_equal(expected_df, real_df)
