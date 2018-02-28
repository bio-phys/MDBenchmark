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
from click import exceptions

import pytest
from mdbenchmark import validate


def test_validate_generate_name():
    """Test that the validate_generate_name function works as expected."""

    with pytest.raises(exceptions.BadParameter) as error:
        validate.validate_generate_name()

    assert str(
        error.value) == 'Please specify the base name of your input files.'

    assert validate.validate_generate_name('md') is None


def test_validate_generate_module():
    """Test that the validate_generate_module function works as expected."""

    with pytest.raises(exceptions.BadParameter) as error:
        validate.validate_generate_module()

    assert str(
        error.value
    ) == 'Please specify which MD engine module to use for the benchmarks.'

    assert validate.validate_generate_module('gromacs/123') is None


def test_validate_generate_number_of_nodes():
    """Test that the validate_generate_number_of_nodes function works as expected."""

    with pytest.raises(exceptions.BadParameter) as error:
        validate.validate_generate_number_of_nodes(min_nodes=6, max_nodes=5)

    assert str(
        error.value
    ) == 'The minimal number of nodes needs to be smaller than the maximal number.'

    assert validate.validate_generate_number_of_nodes(
        min_nodes=1, max_nodes=6) is None


def test_validate_generate_host():
    """Test that the validate_generate_host function works as expected."""

    # Test error without any hostname
    with pytest.raises(exceptions.BadParameter) as error:
        assert validate.validate_generate_host() == (None, False)
    assert str(error.value) == 'Could not find template for host \'None\'.'

    # Test success of existent hostname
    assert validate.validate_generate_host(host='draco', status=True) is None


def test_validate_generate_arguments():
    """Test that the validate_generate_argument function works as expected."""

    assert validate.validate_generate_arguments(
        name='md',
        module='gromacs/123',
        host=('draco', True),
        min_nodes=1,
        max_nodes=6) is None
