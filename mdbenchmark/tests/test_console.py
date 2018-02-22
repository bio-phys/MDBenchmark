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
import pytest
from six import StringIO

from mdbenchmark import console


def test_console_wrapper():
    """Make sure that the console_wrapper function works as expected."""

    # Test that we must pass the same number of placeholders and arguments to
    # the console_wrapper.
    with pytest.raises(ValueError):
        console.console_wrapper('Hello John {}')

    # Test that we can pass a placeholder via args
    fh = StringIO()
    console.console_wrapper('Hello {}', filehandler=fh, args=['John'])
    assert fh.getvalue() == 'Hello John\n'

    # Make sure we can pass positional placeholders via kwargs
    fh = StringIO()
    console.console_wrapper(
        'Starting {count} benchmarks on {host} using {nodes} nodes!',
        filehandler=fh,
        host='draco',
        nodes=123,
        count=5.0)
    output = 'Starting 5.0 benchmarks on draco using 123 nodes!\n'
    assert fh.getvalue() == output


def test_console_info():
    """Test the output of console.info()."""
    fh = StringIO()
    console.info('You have been informed.', filehandler=fh)
    assert fh.getvalue() == 'You have been informed.\n'


def test_console_warn():
    """Test the output of console.warn()."""
    fh = StringIO()
    console.warn('I am not feeling good today.', filehandler=fh)
    assert fh.getvalue() == 'WARNING I am not feeling good today.\n'


def test_console_error():
    """Test the output of console.error()."""
    fh = StringIO()

    with pytest.raises(SystemExit) as error:
        console.error('Does not compute.', filehandler=fh)
    assert fh.getvalue() == 'ERROR Does not compute.\n'
    assert error.type == SystemExit
    assert error.value.code == 1
