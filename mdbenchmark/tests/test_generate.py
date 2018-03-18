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

import pytest
from mdbenchmark import cli
from mdbenchmark.ext.click_test import cli_runner

from .mdengines.test_init import DIR_STRUCTURE


@pytest.mark.parametrize('tpr_file', ('protein.tpr', 'protein'))
def test_generate(cli_runner, monkeypatch, tmpdir, tpr_file):
    """Run an integration test on the generate function.

    Make sure that we accept both `protein` and `protein.tpr` as input files.
    """
    with tmpdir.as_cwd():
        with open('protein.tpr', 'w') as fh:
            fh.write('This is a dummy tpr ;)')

        output = 'Creating benchmark system for gromacs/2016 with GPUs.\n' \
                 'Creating a total of 4 benchmarks, with a run time of 15' \
                 ' minutes each.\nFinished generating all benchmarks.\nYou can' \
                 ' now submit the jobs with mdbenchmark submit.\n'

        # Test that we get a warning, if no module name validation is performed.
        result = cli_runner.invoke(cli.cli, [
            'generate', '--module=gromacs/2016', '--host=draco',
            '--max-nodes=4', '--gpu', '--name={}'.format(tpr_file)
        ])
        assert result.exit_code == 0
        assert result.output == 'WARNING Not performing module name validation. Cannot locate modules available on this host.\n' + output

        # monkeypatch the output of the available modules
        monkeypatch.setattr('mdbenchmark.generate.get_available_modules',
                            lambda: {'gromacs': ['2016']})

        # Test that we can skip module name validation, even if it actually works.
        result = cli_runner.invoke(cli.cli, [
            'generate', '--module=gromacs/2016', '--host=draco',
            '--max-nodes=4', '--gpu', '--name={}'.format(tpr_file),
            '--skip-validation'
        ])
        assert result.exit_code == 0
        assert result.output == 'WARNING Not performing module name validation.\n' + output

        result = cli_runner.invoke(cli.cli, [
            'generate', '--module=gromacs/2016', '--host=draco',
            '--max-nodes=4', '--gpu', '--name={}'.format(tpr_file)
        ])
        assert result.exit_code == 0
        assert result.output == output
        assert os.path.exists('draco_gromacs')
        for i in range(1, 5):
            assert os.path.exists('draco_gromacs/2016_gpu/{}'.format(i))
            assert os.path.exists(
                'draco_gromacs/2016_gpu/{}/protein.tpr'.format(i))
            assert os.path.exists(
                'draco_gromacs/2016_gpu/{}/bench.job'.format(i))

        # Test that we throw an error, if we cannot find the requested module name.
        with tmpdir.as_cwd():
            for k, v in DIR_STRUCTURE.items():
                for k2, v2 in v.items():
                    os.makedirs(os.path.join(k, k2))
                    for v3 in v2:
                        open(os.path.join(k, k2, v3), 'a').close()

            # Prepare path variable that we are going to monkeypatch for
            # `validate.get_available_modules`
            dirs = ':'.join([
                os.path.join(os.getcwd(), x) for x in os.listdir(os.getcwd())
            ])
            monkeypatch.setenv('MODULEPATH', dirs)

            output = 'ERROR There is currently no support for \'doesnotexist/version\'. ' \
                     'Supported MD engines are: gromacs, namd.\n'
            result = cli_runner.invoke(cli.cli, [
                'generate', '--module=doesnotexist/version', '--host=draco',
                '--name={}'.format(tpr_file)
            ])
            assert result.output == output

        output = 'Creating benchmark system for gromacs/2016 with GPUs.\n' \
                 'Creating a total of 3 benchmarks, with a run time of 15 minutes each.\n' \
                 'Finished generating all benchmarks.\n' \
                 'You can now submit the jobs with mdbenchmark submit.\n'
        result = cli_runner.invoke(cli.cli, [
            'generate', '--module=gromacs/2016', '--host=draco',
            '--min-nodes=6', '--max-nodes=8', '--gpu',
            '--name={}'.format(tpr_file)
        ])
        assert result.exit_code == 0
        assert result.output == output
        assert os.path.exists('draco_gromacs')
        for i in range(6, 9):
            assert os.path.exists('draco_gromacs/2016_gpu/{}'.format(i))
            assert os.path.exists(
                'draco_gromacs/2016_gpu/{}/protein.tpr'.format(i))
            assert os.path.exists(
                'draco_gromacs/2016_gpu/{}/bench.job'.format(i))

        # Make sure we pass the correct file name to the job template. It
        # should not contain any file extensions for GROMACS.
        with open('draco_gromacs/2016_gpu/6/bench.job') as f:
            for line in f:
                if not line.startswith('srun'):
                    continue
                assert line.endswith('-deffnm protein')


def test_generate_console_messages(cli_runner, monkeypatch, tmpdir):
    """Test that the CLI for generate prints all error messages as expected."""
    with tmpdir.as_cwd():
        # monkeypatch the output of the available modules
        monkeypatch.setattr('mdbenchmark.generate.get_available_modules',
                            lambda: {'gromacs': ['2016']})

        # Test that we get an error when not supplying a file name
        result = cli_runner.invoke(
            cli.cli, ['generate', '--module=gromacs/2016', '--host=draco'])
        output = 'Usage: cli generate [OPTIONS]\n\nError: Invalid value for ' \
                 '"-n" / "--name": Please specifiy the name of your input files.'

        # Test error message if the TPR file does not exist
        result = cli_runner.invoke(cli.cli, [
            'generate', '--module=gromacs/2016', '--host=draco', '--name=md'
        ])
        output = 'ERROR File md.tpr does not exist, but is needed for GROMACS benchmarks.\n'

        assert result.exit_code == 1
        assert result.output == output

        with open('protein.tpr', 'w') as fh:
            fh.write('This is a dummy tpr!')

        # Test that the minimal number of nodes must be bigger than the maximal number
        result = cli_runner.invoke(cli.cli, [
            'generate', '--module=gromacs/2016', '--host=draco',
            '--name=protein', '--min-nodes=6', '--max-nodes=4'
        ])
        output = 'Usage: cli generate [OPTIONS]\n\nError: Invalid value for ' \
                 '"--min-nodes": The minimal number of nodes needs to be smaller ' \
                 'than the maximal number.\n'
        assert result.exit_code == 2
        assert result.output == output

        # Test error message if we pass an invalid template name
        result = cli_runner.invoke(cli.cli, [
            'generate', '--module=gromacs/2016', '--host=minerva',
            '--name=protein'
        ])
        output = 'Usage: cli generate [OPTIONS]\n\nError: Invalid value for' \
                 ' "--host": Could not find template for host \'minerva\'.\n'
        assert result.exit_code == 2
        assert result.output == output

        # Test error message if we do not pass any module name
        result = cli_runner.invoke(
            cli.cli, ['generate', '--host=draco', '--name=protein'])
        output = 'Usage: cli generate [OPTIONS]\n\nError: Invalid value for ' \
                 '"-m" / "--module": Please specify which MD engine module ' \
                 'to use for the benchmarks.\n'
        assert result.exit_code == 2
        assert result.output == output


def test_generate_namd_experimental_warning(cli_runner, monkeypatch, tmpdir):
    """Test that we print the NAMD experimental warning."""
    with tmpdir.as_cwd():
        for f in ['md.namd', 'md.psf', 'md.pdb']:
            open(f, 'a').close()

        # monkeypatch the output of the available modules
        monkeypatch.setattr('mdbenchmark.generate.get_available_modules',
                            lambda: {'namd': ['123']})

        result = cli_runner.invoke(cli.cli, [
            'generate', '--module=namd/123', '--host=draco', '--name=md'
        ])
        output = 'WARNING NAMD support is experimental. ' \
                 'All input files must be in the current directory. ' \
                 'Parameter paths must be absolute. Only crude file checks are performed!' \
                 'If you use the --gpu option make sure you use the GPU compatible NAMD module!\n' \
                 'Creating benchmark system for namd/123.\n' \
                 'Creating a total of 5 benchmarks, with a run time of 15 ' \
                 'minutes each.\nFinished generating all benchmarks.\nYou can ' \
                 'now submit the jobs with mdbenchmark submit.\n'

        assert result.exit_code == 0
        assert result.output == output
