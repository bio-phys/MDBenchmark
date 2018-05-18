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
import os

from mdbenchmark import cli
from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark.testing import data, datafiles


def test_analyze_gromacs(cli_runner, tmpdir, data):
    """Test that the output is OK when all outputs are fine."""
    with tmpdir.as_cwd():

        result = cli_runner.invoke(cli.cli, [
            'analyze',
            '--directory={}'.format(data['analyze-files-gromacs']),
        ])
        assert result.exit_code == 0
        assert result.output == """           module  nodes   ns/day  run time [min]    gpu   host  ncores
0  gromacs/2016.3      1   98.147              15  False  draco      32
1  gromacs/2016.3      2  178.044              15  False  draco      64
2  gromacs/2016.3      3  226.108              15  False  draco      96
3  gromacs/2016.3      4  246.973              15  False  draco     128
4  gromacs/2016.3      5  254.266              15  False  draco     160
"""


def test_analyze_many_rows(cli_runner, tmpdir, datafiles):
    """Test that pandas does not limit the number of printed rows."""
    with tmpdir.as_cwd():
        open('protein.tpr', 'a').close()

        generate = cli_runner.invoke(cli.cli, [
            'generate', '--module=gromacs/2016.3', '--host=draco',
            '--max-nodes=64', '--name=protein'
        ])

        data = datafiles['analyze_many_rows.out']
        with open(data) as f:
            output = f.readlines()

        result = cli_runner.invoke(cli.cli,
                                   ['analyze', '--directory=draco_gromacs'])

        assert result.exit_code == 0
        assert result.output == ''.join(output)


def test_analze_namd(cli_runner, tmpdir, data):
    with tmpdir.as_cwd():
        result = cli_runner.invoke(
            cli.cli,
            ['analyze', '--directory={}'.format(data['analyze-files-namd'])])
        assert result.exit_code == 0
        assert result.output == """  module  nodes    ns/day  run time [min]    gpu   host  ncores
0   namd      1  0.076328              15  False  draco       1
1   namd      2  0.076328              15  False  draco       1
"""


def test_analyze_with_errors(cli_runner, tmpdir, data):
    """Test that we warn the user of errors in the output files. Also test that we
show a question mark instead of a float in the corresponding cell.
    """
    with tmpdir.as_cwd():

        result = cli_runner.invoke(cli.cli, [
            'analyze',
            '--directory={}'.format(data['analyze-files-w-errors']),
        ])
        assert result.exit_code == 0
        assert result.output == """WARNING We were not able to gather informations for all systems. Systems marked with question marks have either crashed or were not started yet.
           module  nodes   ns/day  run time [min]    gpu   host ncores
0  gromacs/2016.3      1   98.147              15  False  draco     32
1  gromacs/2016.3      2  178.044              15  False  draco     64
2  gromacs/2016.3      3  226.108              15  False  draco     96
3  gromacs/2016.3      4  246.973              15  False  draco    128
4  gromacs/2016.3      5  254.266              15  False  draco    160
5  gromacs/2016.3      6        ?              15  False  draco      ?
6  gromacs/2016.3      7        ?              15  False  draco    160
7  gromacs/2016.3      8  254.266              15  False  draco      ?
"""


def test_analyze_plot(cli_runner, tmpdir, data):
    with tmpdir.as_cwd():

        result = cli_runner.invoke(cli.cli, [
            'analyze',
            '--directory={}'.format(data['analyze-files-gromacs'], '--plot'),
        ])
        assert result.exit_code == 0
        assert result.output == """           module  nodes   ns/day  run time [min]    gpu   host  ncores
0  gromacs/2016.3      1   98.147              15  False  draco      32
1  gromacs/2016.3      2  178.044              15  False  draco      64
2  gromacs/2016.3      3  226.108              15  False  draco      96
3  gromacs/2016.3      4  246.973              15  False  draco     128
4  gromacs/2016.3      5  254.266              15  False  draco     160
"""
        os.path.isfile("runtimes.pdf")


def test_analyze_console_messages(cli_runner, tmpdir):
    """Test that the CLI for analyze prints all error messages as expected."""
    with tmpdir.as_cwd():
        # Test error message if the TPR file does not exist
        result = cli_runner.invoke(cli.cli,
                                   ['analyze', '--directory=look_here/'])
        output = "ERROR There is no data for the given path.\n"
        assert result.exit_code == 1
        assert result.output == output
