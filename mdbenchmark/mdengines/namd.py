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


def parse_ns_day(fh):
    """parse nanoseconds per day from a NAMD log file

    Parameters
    ----------
    fh : str / filehandle
        filename or string of log file to read

    Returns
    -------
    float
        nanoseconds per day
    """
    lines = fh.readlines()

    for line in lines:
        if 'Benchmark time' in line:
            return 1 / float(line.split()[7])

    return np.nan


def parse_ncores(fh):
    """parse number of cores from a NAMD log file

    Parameters
    ----------
    fh : str / filehandle
        filename or string of log file to read

    Returns
    -------
    float
        number of cores job was run on
    """
    lines = fh.readlines()

    for line in lines:
        if 'Benchmark time' in line:
            return int(line.split()[3])

    return np.nan


def analyze_run(sim):
    """
    Analyze Performance data of a NAMD simulation
    """
    ns_day = np.nan
    ncores = np.nan

    # search all output files
    output_files = glob(os.path.join(sim.relpath, '*out*'))
    if output_files:
        with open(output_files[0]) as fh:
            ns_day = parse_ns_day(fh)
            fh.seek(0)
            ncores = parse_ncores(fh)

    # module = sim.categories['module']

    return (sim.categories['module'], sim.categories['nodes'], ns_day,
            sim.categories['time'], sim.categories['gpu'],
            sim.categories['host'], ncores)


def write_bench(top, tmpl, nodes, gpu, module, name, host, time):
    """ Writes a single namd benchmark file and the respective sim object
    """
    # Strip the file extension, if we were given one.
    # This makes the usage of `mdbenchmark generate` equivalent between NAMD and GROMACS.
    if name.endswith('.namd'):
        name = name[:-5]
    sim = mds.Sim(
        top['{}/'.format(nodes)],
        categories={
            'module': module,
            'gpu': gpu,
            'nodes': nodes,
            'host': host,
            'time': time,
            'name': name,
            'started': False
        })

    # Copy input files
    namd = '{}.namd'.format(name)
    psf = '{}.psf'.format(name)
    pdb = '{}.pdb'.format(name)

    with open(namd) as fh:
        analyze_namd_file(fh)
        fh.seek(0)

    copyfile(namd, sim[namd].relpath)
    copyfile(psf, sim[psf].relpath)
    copyfile(pdb, sim[pdb].relpath)

    # Add some time buffer to the requested time. Otherwise the queuing system
    # kills the jobs before NAMD can finish
    formatted_time = '{:02d}:{:02d}:00'.format(*divmod(time + 5, 60))
    # engine switch to pick the right submission statement in the templates
    md_engine = "namd"
    # create bench job script
    script = tmpl.render(
        name=name,
        gpu=gpu,
        module=module,
        mdengine=md_engine,
        n_nodes=nodes,
        time=time,
        formatted_time=formatted_time)

    with open(sim['bench.job'].relpath, 'w') as fh:
        fh.write(script)


def analyze_namd_file(fh):
    """ Check whether the NAMD config file has any relative imports or variables
    """
    lines = fh.readlines()

    for line in lines:
        # Continue if we do not need to do anything with the current line
        if ('parameters' not in line) and ('coordinates' not in line) and (
                'structure' not in line):
            continue

        path = line.split()[1]
        if '$' in path:
            console.error(
                'Variable Substitutions are not allowed in NAMD files!')
        if '..' in path:
            console.error('Relative file paths are not allowed in NAMD files!')
        if '/' not in path or ('/' in path and not path.startswith('/')):
            console.error('No absolute path detected in NAMD file!')


def check_input_file_exists(name):
    """Check and append the correct file extensions for the NAMD module.
    """
    # Check whether the needed files are there.
    for extension in ['namd', 'psf', 'pdb']:
        if name.endswith('.{}'.format(extension)):
            name = name[:-1 + len(extension)]

        fn = '{}.{}'.format(name, extension)
        if not os.path.exists(fn):
            console.error(
                "File {} does not exist, but is needed for NAMD benchmarks.",
                fn)

    return


def cleanup_before_restart(sim):
    white_list = ['.*/bench\.job', '.*\.namd', '.*\.psf', '.*\.pdb']
    white_list = [re.compile(fname) for fname in white_list]

    files_found = []
    for fname in sim.leaves:
        keep = False
        for wl in white_list:
            if wl.match(str(fname)):
                keep = True
        if keep:
            continue

        files_found.append(fname.relpath)

    for fn in files_found:
        os.remove(fn)
