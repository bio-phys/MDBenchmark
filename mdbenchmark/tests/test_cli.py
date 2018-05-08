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

from mdbenchmark import cli
from mdbenchmark.ext.click_test import cli_runner


def test_aliasedgroup_unknown_command(cli_runner):
    """Test that we return an error, when invoking an unknown command."""
    result = cli_runner.invoke(cli.cli, [
        'unknown_command',
    ])
    assert result.exit_code == 2
    output = 'Usage: cli [OPTIONS] COMMAND [ARGS]...\n\n' \
             'Error: Sub command unknown: unknown_command\n'
    assert result.output == output


def test_aliasedgroup_known_alias(cli_runner):
    """Test that we can use all defined aliases."""
    result = cli_runner.invoke(cli.cli, [
        'start',
    ])
    assert result.exit_code == 1
