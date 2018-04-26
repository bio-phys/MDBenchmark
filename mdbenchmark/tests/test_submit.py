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

from mdbenchmark import cli
from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark.mdengines import gromacs
from mdbenchmark.submit import get_batch_command
from mdbenchmark.testing import data


def test_get_batch_command(capsys, monkeypatch, tmpdir):
    """Test that the get_engine_command works correctly.

    It should exit if no batching system was found.
    """
    # Test fail state
    output = 'ERROR Was not able to find a batch system. ' \
             'Are you trying to use this package on a host with a queuing system?\n'
    with pytest.raises(SystemExit):
        get_batch_command()
        out, err = capsys.readouterr()
        assert out == output

    # Test non-fail state
    monkeypatch.setattr('mdbenchmark.submit.glob', lambda x: ['qsub'])
    assert get_batch_command()


def test_submit_resubmit(cli_runner, monkeypatch, tmpdir, data):
    """Test that we cannot submit a benchmark system that was already submitted,
       unless we force it.
    """
    with tmpdir.as_cwd():
        # Test that we get an error if we try to point the submit function to
        # an non-existent path.
        result = cli_runner.invoke(cli.cli, [
            'submit',
            '--directory=look_here/',
        ])
        assert result.exit_code == 1
        assert result.output == 'ERROR No benchmarks found.\n'

        # Test that we get an error if we try to start benchmarks that were
        # already started once.
        result = cli_runner.invoke(cli.cli, [
            'submit',
            '--directory={}'.format(data['analyze-files-gromacs']),
        ])
        assert result.exit_code == 1
        assert result.output == 'ERROR All generated benchmarks were already ' \
                                'started once. You can force a restart with ' \
                                '--force.\n'

        # Test that we can force restart already run benchmarks.
        # Monkeypatch a few functions
        monkeypatch.setattr('subprocess.call', lambda x: True)
        monkeypatch.setattr('mdbenchmark.submit.get_batch_command',
                            lambda: 'sbatch')
        monkeypatch.setattr('mdbenchmark.submit.detect_md_engine',
                            lambda x: gromacs)
        monkeypatch.setattr('mdbenchmark.submit.cleanup_before_restart',
                            lambda engine, sim: True)
        output = 'Submitting a total of 5 benchmarks.\n' \
                 'Submitted all benchmarks. Run mdbenchmark analyze once ' \
                 'they are finished to get the results.\n'
        result = cli_runner.invoke(cli.cli, [
            'submit', '--directory={}'.format(data['analyze-files-gromacs']),
            '--force'
        ])
        assert result.exit_code == 0
        assert result.output == output
