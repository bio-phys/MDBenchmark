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
import re
from glob import glob
from shutil import copyfile

import mdsynthesis as mds
import numpy as np

from .. import console
from .namd import analyze_namd_file


def prepare_gromacs_benchmark(name, *args, **kwargs):
    sim = kwargs['sim']

    full_filename = name + '.tpr'
    if name.endswith('.tpr'):
        full_filename = name
        name = name[:-4]

    copyfile(full_filename, sim[full_filename].relpath)

    return name


def prepare_namd_benchmark(name, *args, **kwargs):
    sim = kwargs['sim']

    if name.endswith('.namd'):
        name = name[:-5]

    namd = '{}.namd'.format(name)
    psf = '{}.psf'.format(name)
    pdb = '{}.pdb'.format(name)

    with open(namd) as fh:
        analyze_namd_file(fh)
        fh.seek(0)

    copyfile(namd, sim[namd].relpath)
    copyfile(psf, sim[psf].relpath)
    copyfile(pdb, sim[pdb].relpath)

    return name


def prepare_benchmark(engine, name, *args, **kwargs):
    if engine.NAME == 'gromacs':
        name = prepare_gromacs_benchmark(name, *args, **kwargs)
    elif engine.NAME == 'namd':
        name = prepare_namd_benchmark(name, *args, **kwargs)

    return name


def write_benchmark(engine, base_directory, template, nodes, gpu, module, name,
                    host, time):
    """Generate a benchmark folder with the respective Sim object."""
    # Create the `mds.Sim` object
    sim = mds.Sim(base_directory['{}/'.format(nodes)])

    # Do MD engine specific things. Here we also format the name.
    name = prepare_benchmark(engine=engine, name=name, sim=sim)

    # Add categories to the `Sim` object
    sim.categories = {
        'module': module,
        'gpu': gpu,
        'nodes': nodes,
        'host': host,
        'time': time,
        'name': name,
        'started': False
    }

    # Add some time buffer to the requested time. Otherwise the queuing system
    # kills the job before the benchmark is finished
    formatted_time = '{:02d}:{:02d}:00'.format(*divmod(time + 5, 60))

    # Create benchmark job script
    script = template.render(
        name=name,
        gpu=gpu,
        module=module,
        mdengine=engine.NAME,
        n_nodes=nodes,
        time=time,
        formatted_time=formatted_time)

    # Write the actual job script that is going to be submitted to the cluster
    with open(sim['bench.job'].relpath, 'w') as fh:
        fh.write(script)
