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

from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark.mdengines import detect_md_engine, gromacs, namd


def test_detect_md_engine(cli_runner):
    """Test that the function `detect_md_engine` works as expected."""

    engine = detect_md_engine('gromacs/2016.3')
    assert engine.__name__ == 'mdbenchmark.mdengines.gromacs'

    engine = detect_md_engine('namd/123')
    assert engine.__name__ == 'mdbenchmark.mdengines.namd'

    @click.group()
    def test_cli():
        pass

    @test_cli.command()
    def test():
        detect_md_engine('MagicMDEngine/123')

    output = 'ERROR No suitable engine detected for \'MagicMDEngine/123\'. ' \
             'Known engines are: gromacs, namd.\n'
    result = cli_runner.invoke(test_cli, ['test'])
    assert result.exit_code == 1
    assert result.output == output
