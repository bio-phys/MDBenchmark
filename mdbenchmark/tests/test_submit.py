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

from mdbenchmark import cli
from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark.submit import get_batch_command
from mdbenchmark.testing import data


def test_get_batch_command(cli_runner, monkeypatch, tmpdir):
    """Test that the get_engine_command works correctly.

    It should exit if no batching system was found.
    """

    # The following was taken from the basic testing example from the Click
    # documentation: http://click.pocoo.org/6/testing/#basic-testing
    # We need to do this, because `get_engine_command()` uses `click.echo` to
    # display an error message and we want to test its value.
    @click.group()
    def test_cli():
        pass

    @test_cli.command()
    def test():
        get_batch_command()

    # Test fail state
    output = 'ERROR Was not able to find a batch system. ' \
             'Are you trying to use this package on a host with a queuing system?\n'
    result = cli_runner.invoke(test_cli, ['test'])
    assert result.exit_code == 1
    assert result.output == output

    # Test non-fail state
    monkeypatch.setattr('mdbenchmark.submit.glob', lambda x: ['qsub'])
    result = cli_runner.invoke(test_cli, ['test'])
    assert result.exit_code == 0


class DummyEngine(object):
    @staticmethod
    def cleanup_before_restart(sim):
        pass


def test_submit_resubmit(cli_runner, monkeypatch, tmpdir, data):
    """Test that we cannot submit a benchmark system that was already submitted,
       unless we force it.
    """

    # Define dummy function, so we can monkeypatch `subprocess.call` and
    # `mdbenchmark.utils.cleanup_before_restart`.
    def call(arg):
        return DummyEngine

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
        assert result.output == 'ERROR All generated benchmarks were already' \
                                ' started once. You can force a restart with' \
                                ' --force.\n'

        # Test that we can force restart already run benchmarks.
        # Monkeypatch a few functions
        monkeypatch.setattr('subprocess.call', call)
        monkeypatch.setattr('mdbenchmark.submit.get_batch_command',
                            lambda: 'sbatch')
        # We need to patch the cleanup, as we otherwise delete our own test
        # files
        monkeypatch.setattr('mdbenchmark.submit.detect_md_engine', call)
        output = 'Submitting a total of 5 benchmarks.\n' \
                 'Submitted all benchmarks. Run mdbenchmark analyze once' \
                 ' they are finished to get the results.\n'
        result = cli_runner.invoke(cli.cli, [
            'submit', '--directory={}'.format(data['analyze-files-gromacs']),
            '--force'
        ])
        assert result.exit_code == 0
        assert result.output == output
