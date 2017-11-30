import os
from glob import glob

import click
import numpy as np
from mdbenchmark.utils import (calc_slope_intercept, cleanup_before_restart,
                               get_possible_hosts, guess_host, lin_func,
                               normalize_host, print_possible_hosts)
from numpy.testing import assert_array_equal

import pytest


def test_get_possible_hosts():
    """Assert that we can retrieve the correct number of hosts.
    These are determined by the job files currently shipped
    with this package.
    """
    hosts = get_possible_hosts()
    assert isinstance(hosts, list)
    assert len(hosts) == 2


def test_print_possible_hosts(capsys):
    """Assert that we the printing of available hosts works as expected."""
    print_possible_hosts()
    out, err = capsys.readouterr()

    assert out == 'Available host templates:\ndraco\nhydra\n'


def test_guess_host():
    """Assert that `guess_host()` does not recognize a random machine as a host.

    Note: this test may fail on a machine that, by accident, is called like a
    host file that we provide.
    """
    assert guess_host() is None


def test_monkeypatch_guess_host(monkeypatch):
    """Assert that `guess_host()` will correctly assign the hostname to a host
    file.
    """
    host = 'HPC_cluster'
    monkeypatch.setattr('mdbenchmark.utils.socket.gethostname', lambda: host)
    monkeypatch.setattr('mdbenchmark.utils.get_possible_hosts', lambda: [host])
    assert guess_host() == host


def test_normalize_host(monkeypatch):
    """Test `normalize_host()`."""
    with pytest.raises(click.BadParameter):
        normalize_host(None)

    host = 'HPC_cluster'
    monkeypatch.setattr('mdbenchmark.utils.guess_host', lambda: host)
    assert normalize_host(host) == host


def test_lin_func():
    """Test `lin_func()`."""
    m, x, b = [5, 3, 2]

    assert_array_equal(lin_func(m, x, b), (m * x) + b)


def test_calc_slope_intercept():
    """Test `calc_slope_intercept()`"""
    x1, y1 = [1, 1]
    x2, y2 = [2, 2]
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - (x1 * slope)

    slope_intercept = calc_slope_intercept(x1, y1, x2, y2)

    assert_array_equal(slope_intercept, np.hstack([slope, intercept]))


def test_cleanup_before_restart(tmpdir):
    """Test that the cleanup of each directory works as intended."""
    FILES_TO_DELETE = [
        'job_thing.err.123job', 'job_thing.out.123job', 'md.log', 'md.xtc',
        'md.cpt', 'md.edr', 'job.po12345', 'job.o12345', 'md.out'
    ]
    FILES_TO_KEEP = ['md.mdp', 'md.tpr']

    # Create temporary directory
    tmp = tmpdir.mkdir("mdbenchmark")

    # Create empty files
    for f in FILES_TO_DELETE + FILES_TO_KEEP:
        open('{}/{}'.format(tmp, f), 'a').close()

    # Run the cleanup script
    cleanup_before_restart(tmp)

    # Look for files that were left
    files_found = []
    for f in FILES_TO_KEEP:
        files_found.extend(glob(os.path.join(str(tmp), f)))

    # Get rid of the `tmp` path and only compare the actual filenames
    assert FILES_TO_KEEP == [x[len(str(tmp)) + 1:] for x in files_found]
