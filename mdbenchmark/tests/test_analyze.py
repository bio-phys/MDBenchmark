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
from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark import cli
from mdbenchmark.testing import data


def test_analyze(cli_runner, tmpdir, data):
    with tmpdir.as_cwd():

        result = cli_runner.invoke(cli.cli, [
            'analyze',
            '--directory={}'.format(data['analyze-files']),
        ])
        assert result.exit_code == 0
        assert result.output == """          gromacs nodes   ns/day run time [min]    gpu   host
0  gromacs/2016.3     1   98.147             15  False  draco
1  gromacs/2016.3     2  178.044             15  False  draco
2  gromacs/2016.3     3  226.108             15  False  draco
3  gromacs/2016.3     4  246.973             15  False  draco
4  gromacs/2016.3     5  254.266             15  False  draco
"""
