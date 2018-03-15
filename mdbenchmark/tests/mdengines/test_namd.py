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
from glob import glob

import click
import datreant.core as dtr
import numpy as np
import pytest
from six.moves import StringIO

from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark.mdengines import namd


@pytest.fixture
def log():
    return StringIO("""
    Info: Benchmark time: 1 CPUs 1.13195 s/step 13.1013 days/ns 2727.91 MB memory
    """)


@pytest.fixture
def empty_log():
    return StringIO("""
    not the log you are looking for
    """)


def test_parse_ns_day(log):
    assert namd.parse_ns_day(log) == 1 / 13.1013


def test_parse_ncores(log):
    assert namd.parse_ncores(log) == 1


@pytest.mark.parametrize('parse', (namd.parse_ncores, namd.parse_ns_day))
def test_parse_empty_log(empty_log, parse):
    assert np.isnan(parse(empty_log))


@pytest.fixture
def sim(tmpdir_factory):
    folder = tmpdir_factory.mktemp('simulation')
    return dtr.Treant(
        str(folder),
        categories={
            'nodes': 42,
            'host': 'foo',
            'gpu': False,
            'version': 'bar'
        })


def test_check_file_extension(cli_runner, tmpdir):
    """Test that we check for all files needed to run NAMD benchmarks."""

    @click.group()
    def test_cli():
        pass

    @test_cli.command()
    def test():
        namd.check_input_file_exists('md')

    output = 'ERROR File md.namd does not exist, but is needed for NAMD benchmarks.\n'
    result = cli_runner.invoke(test_cli, ['test'])
    assert result.exit_code == 1
    assert result.output == output

    NEEDED_FILES = ['md.namd', 'md.psf', 'md.pdb']
    with tmpdir.as_cwd():
        # Create files first
        for fn in NEEDED_FILES:
            with open(fn, 'w') as fh:
                fh.write('dummy file')

        result = cli_runner.invoke(test_cli, ['test'])
        assert result.exit_code == 0


def test_analyze_namd_file(cli_runner, tmpdir):
    """Test that we check the `.namd` file as expected."""

    @click.group()
    def test_cli():
        pass

    @test_cli.command()
    def test():
        with open('md.namd') as fh:
            namd.analyze_namd_file(fh)

    with tmpdir.as_cwd():
        # Make sure that we do not throw any error when everything is fine!
        with open('md.namd', 'w') as fh:
            fh.write('dummy file')
        result = cli_runner.invoke(test_cli, ['test'])
        assert result.exit_code == 0
        assert result.output == ''

        # Assert that we fail, when a relative path is given.
        with open('md.namd', 'w') as fh:
            fh.write('parameters ./relative/path/')
        output = 'ERROR No absolute path detected in NAMD file!\n'
        result = cli_runner.invoke(test_cli, ['test'])
        assert result.exit_code == 1
        assert result.output == output

        # Fail if we do not give ANY absolute path.
        with open('md.namd', 'w') as fh:
            fh.write('parameters abc')
        output = 'ERROR No absolute path detected in NAMD file!\n'
        result = cli_runner.invoke(test_cli, ['test'])
        assert result.exit_code == 1
        assert result.output == output

        # Fail if we do not give ANY absolute path.
        with open('md.namd', 'w') as fh:
            fh.write('coordinates ../another/relative/path')
        output = 'ERROR Relative file paths are not allowed in NAMD files!\n'
        result = cli_runner.invoke(test_cli, ['test'])
        assert result.exit_code == 1
        assert result.output == output

        # Fail if we do not give ANY absolute path.
        with open('md.namd', 'w') as fh:
            fh.write('structure $')
        output = 'ERROR Variable Substitutions are not allowed in NAMD files!\n'
        result = cli_runner.invoke(test_cli, ['test'])
        assert result.exit_code == 1
        assert result.output == output


def test_cleanup_before_restart(tmpdir):
    """Test that the cleanup of each directory works as intended for NAMD."""
    FILES_TO_DELETE = [
        'job_thing.err.123job', 'job_thing.out.123job', 'job.po12345',
        'job.o12345', 'benchmark.out'
    ]
    FILES_TO_KEEP = ['md.namd', 'md.pdb', 'md.psf', 'bench.job']

    # Create temporary directory
    tmp = tmpdir.mkdir("mdbenchmark")

    # Create empty files
    for f in FILES_TO_DELETE + FILES_TO_KEEP:
        open('{}/{}'.format(tmp, f), 'a').close()

    # Run the cleanup script
    namd.cleanup_before_restart(dtr.Tree(tmp.strpath))

    # Look for files that were left
    files_found = []
    for f in FILES_TO_KEEP:
        files_found.extend(glob(os.path.join(tmp.strpath, f)))

    # Get rid of the `tmp` path and only compare the actual filenames
    assert FILES_TO_KEEP == [x[len(str(tmp)) + 1:] for x in files_found]
