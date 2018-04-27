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

import jinja2
import numpy as np
from numpy.testing import assert_equal

from mdbenchmark import utils
from mdbenchmark.ext.click_test import cli_runner


def test_mdbenchmark_template_environment_variable(monkeypatch):
    """Test that we can set a custom path via environment variable MDBENCHMARK_TEMPLATES."""
    try:
        from importlib import reload
    except ImportError:
        from imp import reload

    custom_path = '/this/is/a/custom/path'
    monkeypatch.setenv('MDBENCHMARK_TEMPLATES', custom_path)
    reload(utils)
    from mdbenchmark.utils import _loaders
    for path in _loaders:
        if isinstance(path, jinja2.loaders.FileSystemLoader):
            assert path.searchpath[0] in [
                '{}/.config/MDBenchmark'.format(os.getenv('HOME')),
                custom_path, '/etc/xdg/MDBenchmark'
            ]


def test_get_possible_hosts():
    """Assert that we can retrieve the correct number of hosts.
    These are determined by the job files currently shipped
    with this package.
    """
    hosts = utils.get_possible_hosts()
    assert isinstance(hosts, list)
    assert len(hosts) == 2


def test_print_possible_hosts(capsys):
    """Assert that we the printing of available hosts works as expected."""
    utils.print_possible_hosts()
    out, err = capsys.readouterr()

    assert out == 'Available host templates:\ndraco\nhydra\n'


def test_guess_host():
    """Assert that `guess_host()` does not recognize a random machine as a host.

    Note: this test may fail on a machine that, by accident, is called like a
    host file that we provide.
    """
    assert utils.guess_host() is None


def test_monkeypatch_guess_host(monkeypatch):
    """Assert that `guess_host()` will correctly assign the hostname to a host
    file.
    """
    host = 'HPC_cluster'
    monkeypatch.setattr('mdbenchmark.utils.socket.gethostname', lambda: host)
    monkeypatch.setattr('mdbenchmark.utils.get_possible_hosts', lambda: [host])
    assert utils.guess_host() == host


def test_retrieve_host_template(monkeypatch):
    """Test `retrieve_host_template` utility function."""

    # Check template name that we supply with the package
    assert utils.retrieve_host_template('draco') is not None

    # Check that the user can define some custom template
    monkeypatch.setattr('mdbenchmark.utils.ENV.get_template',
                        lambda x: 'minerva')
    assert utils.retrieve_host_template('minerva') == 'minerva'


def test_lin_func():
    """Test `lin_func()`."""
    m, x, b = [5, 3, 2]

    assert_equal(utils.lin_func(m, x, b), (m * x) + b)


def test_calc_slope_intercept():
    """Test `calc_slope_intercept()`"""
    x1, y1 = [1, 1]
    x2, y2 = [2, 2]
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - (x1 * slope)

    slope_intercept = utils.calc_slope_intercept(x1, y1, x2, y2)

    assert_equal(slope_intercept, np.hstack([slope, intercept]))


def test_guess_ncores(capsys, monkeypatch):
    """Test that we can guess the correct number of cores on the supported
    systems.
    """

    def dummy(arg):
        return 'ABC'

    # Test on Linux
    monkeypatch.setattr('mdbenchmark.utils.sys.platform', 'linux')
    monkeypatch.setattr(
        'mdbenchmark.utils._cat_proc_cpuinfo_grep_query_sort_uniq', dummy)
    assert utils.guess_ncores() == 9

    # Test on Darwin
    monkeypatch.setattr('mdbenchmark.utils.sys.platform', 'darwin')
    monkeypatch.setattr('mdbenchmark.utils.mp.cpu_count', lambda: 10)
    assert utils.guess_ncores() == 5

    # Test on some unknown platform
    monkeypatch.setattr('mdbenchmark.utils.sys.platform', 'starlord')
    output = 'WARNING Could not guess number of physical cores. ' \
             'Assuming there is only 1 core per node.\n'

    utils.guess_ncores()
    out, err = capsys.readouterr()
    assert out == output
