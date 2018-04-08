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

import datreant.core as dtr
import mdsynthesis as mds

import pytest
from mdbenchmark.mdengines import gromacs, namd, utils
from mdbenchmark.utils import retrieve_host_template


@pytest.mark.parametrize('engine, input_name, extensions',
                         [(gromacs, 'md.tpr', ['tpr']),
                          (namd, 'md.namd', ['namd', 'pdb', 'psf'])])
def test_prepare_benchmark(engine, input_name, extensions, tmpdir):
    """Test that the preparation functions of all supported MD engines work."""
    with tmpdir.as_cwd():
        for ext in extensions:
            open('md.{}'.format(ext), 'a').close()

        sim = mds.Sim('./{}'.format(engine))
        name = engine.prepare_benchmark(input_name, sim=sim)

        assert name == 'md'
        for ext in extensions:
            assert os.path.exists('./{}/md.{}'.format(engine, ext))


@pytest.mark.parametrize(
    'engine, module, input_name, extensions',
    [(gromacs, 'gromacs/5.1.4', 'md.tpr', ['tpr']),
     (namd, 'namd/2.12', 'md.namd', ['namd', 'pdb', 'psf'])])
@pytest.mark.parametrize('gpu', (True, False))
def test_write_benchmark(engine, gpu, module, input_name, extensions, tmpdir):
    """Test that the write_benchmark works as expected."""
    host = 'draco'
    base_dirname = '{}_{}'.format(host, engine)
    nodes = 5
    with tmpdir.as_cwd():
        base_directory = dtr.Tree(base_dirname)

        for ext in extensions:
            open('md.{}'.format(ext), 'a').close()

        template = retrieve_host_template('draco')
        utils.write_benchmark(engine, base_directory, template, nodes, gpu,
                              module, input_name, host, 15)

        assert os.path.exists(base_dirname)
        assert os.path.exists(
            os.path.join(base_dirname, '{}'.format(nodes), input_name))

        with open(
                os.path.join(base_dirname, '{}'.format(nodes), 'bench.job'),
                'r') as f:
            for line in f:
                if '#SBATCH -J' in line:
                    assert line == '#SBATCH -J {}\n'.format('md')
                if '--partition=' in line:
                    if gpu:
                        assert line == '#SBATCH --partition=gpu\n'
                    else:
                        assert line == '#SBATCH --partition=express\n'
                if '--nodes=' in line:
                    assert line == '#SBATCH --nodes={}\n'.format(nodes)
                if '--time=' in line:
                    assert line == '#SBATCH --time={}\n'.format('00:20:00')
                if 'module load {}/'.format(engine) in line:
                    assert line == 'module load {}\n'.format(module)
                if 'srun' in line:
                    if engine == 'gromacs':
                        assert line == 'srun gmx_mpi mdrun -v -maxh 0.25 -deffnm md'
                    elif engine == 'namd':
                        assert line == 'srun namd2 md.namd'
