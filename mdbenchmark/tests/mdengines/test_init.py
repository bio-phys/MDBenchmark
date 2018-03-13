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

import click
import pytest

from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark.mdengines import (detect_md_engine, get_available_modules,
                                   gromacs, namd, validate_module_name)

DIR_STRUCTURE = {
    'applications': {
        'gromacs': ['2016.4', '5.1.4-plumed2.3', '2018.1', '.12345-version'],
        'namd': ['123', '456'],
        'amber': ['13', '14', '15']
    },
    'visualization': {
        'vmd': ['1.9.3', '1.9.4']
    }
}


def test_detect_md_engine(cli_runner):
    """Test that we only accept supported MD engines."""

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

    output = 'ERROR There is currently no support for \'MagicMDEngine/123\'. ' \
             'Supported MD engines are: gromacs, namd.\n'
    result = cli_runner.invoke(test_cli, ['test'])
    assert result.exit_code == 1
    assert result.output == output


def test_validation(monkeypatch, tmpdir, cli_runner):
    """Test that we retrieve the correct module versions.

       Names are retrieved from a given path and the module names and versions
       are validated.
    """

    @click.group()
    def test_cli():
        pass

    @test_cli.command()
    def test():
        validate_module_name('wrong-format')

    with tmpdir.as_cwd():
        for k, v in DIR_STRUCTURE.items():
            for k2, v2 in v.items():
                os.makedirs(os.path.join(k, k2))
                for v3 in v2:
                    open(os.path.join(k, k2, v3), 'a').close()

        # Make sure we return None when we cannot find the environment variable
        assert get_available_modules() is None
        # Test the same thing for the `validate_module_name` function
        assert validate_module_name('gromacs/123') is None

        # Prepare path variable that we are going to monkeypatch for
        # `validate.get_available_modules`
        dirs = ':'.join(
            [os.path.join(os.getcwd(), x) for x in os.listdir(os.getcwd())])
        monkeypatch.setenv('MODULEPATH', dirs)
        modules = get_available_modules()

        # Assert that the correct modules and their versions are returned.
        assert set(modules['gromacs']) == set(
            ['2016.4', '5.1.4-plumed2.3', '2018.1'])
        assert set(modules['namd']) == set(['123', '456'])

        # Make sure we return a boolean if the module is available or not.
        assert not validate_module_name('gromacs/123')
        assert validate_module_name('gromacs/2018.1')

        output = 'ERROR We were not able to determine the module name.\n'
        result = cli_runner.invoke(test_cli, ['test'])
        assert result.exit_code == 1
        assert result.output == output
