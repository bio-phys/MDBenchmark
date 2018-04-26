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

FILES_TO_KEEP = {
    'gromacs': ['.*/bench\.job', '.*\.tpr', '.*\.mdp'],
    'namd': ['.*/bench\.job', '.*\.namd', '.*\.psf', '.*\.pdb']
}

PARSE_ENGINE = {
    'gromacs': {
        'performance': 'Performance',
        'performance_return': lambda line: float(line.split()[1]),
        'ncores': 'Running on',
        'ncores_return': lambda line: int(line.split()[6]),
        'analyze': '[!#]*log*'
    },
    'namd': {
        'performance': 'Benchmark time',
        'performance_return': lambda line: 1 / float(line.split()[7]),
        'ncores': 'Benchmark time',
        'ncores_return': lambda line: int(line.split()[3]),
        'analyze': '*out*'
    }
}


def parse_ns_day(engine, fh):
    """Parse the performance (ns/day) from any MD engine log file.

    Parameters
    ----------
    fh : str / filehandle
        Filename or string of log file to read

    Returns
    -------
    float / np.nan
        Nanoseconds per day or NaN
    """
    lines = fh.readlines()

    for line in lines:
        if PARSE_ENGINE[engine.NAME]['performance'] in line:
            return PARSE_ENGINE[engine.NAME]['performance_return'](line)

    return np.nan


def parse_ncores(engine, fh):
    """Parse the number of cores from any MD engine log file.

    Parameters
    ----------
    fh : str / filehandle
        Filename or string of log file to read

    Returns
    -------
    int / np.nan
        Number of cores job was run on or NaN
    """
    lines = fh.readlines()

    for line in lines:
        if PARSE_ENGINE[engine.NAME]['ncores'] in line:
            return PARSE_ENGINE[engine.NAME]['ncores_return'](line)

    return np.nan


def analyze_run(engine, sim):
    """
    Analyze performance data from a simulation run with any MD engine.
    """
    ns_day = np.nan
    ncores = np.nan

    # search all output files
    output_files = glob(
        os.path.join(sim.relpath, PARSE_ENGINE[engine.NAME]['analyze']))
    if output_files:
        with open(output_files[0]) as fh:
            ns_day = parse_ns_day(engine, fh)
            fh.seek(0)
            ncores = parse_ncores(engine, fh)

    # Backward compatibility to benchmark systems created with older versions
    # of MDBenchmark
    if 'time' not in sim.categories:
        sim.categories['time'] = 0
    if 'module' in sim.categories:
        module = sim.categories['module']
    else:
        module = sim.categories['version']

    return (module, sim.categories['nodes'], ns_day, sim.categories['time'],
            sim.categories['gpu'], sim.categories['host'], ncores)


def cleanup_before_restart(engine, sim):
    whitelist = FILES_TO_KEEP[engine.NAME]
    whitelist = [re.compile(fname) for fname in whitelist]

    files_found = []
    for fname in sim.leaves:
        keep = False
        for wl in whitelist:
            if wl.match(str(fname)):
                keep = True
        if keep:
            continue

        files_found.append(fname.relpath)

    for fn in files_found:
        os.remove(fn)


def write_benchmark(engine, base_directory, template, nodes, gpu, module, name,
                    host, time):
    """Generate a benchmark folder with the respective Sim object."""
    # Create the `mds.Sim` object
    sim = mds.Sim(base_directory['{}/'.format(nodes)])

    # Do MD engine specific things. Here we also format the name.
    name = engine.prepare_benchmark(name=name, sim=sim)

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
