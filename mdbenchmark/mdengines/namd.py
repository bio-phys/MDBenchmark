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
import warnings
from glob import glob
from shutil import copyfile

import click
import datreant.core as dtr
import mdsynthesis as mds
import numpy as np
from jinja2.exceptions import TemplateNotFound
from six import string_types


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

    # search all output files and ignore GROMACS backup files
    output_files = glob(os.path.join(sim.relpath, '[!#]*out*'))
    if output_files:
        with open(output_files[0]) as fh:
            ns_day = parse_ns_day(fh)
            fh.seek(0)
            ncores = parse_ncores(fh)

    # Backward compatibility to previously created mdbenchmark systems
    if 'time' not in sim.categories:
        sim.categories['time'] = 0

    # backward compatibility
    if 'module' in sim.categories:
        module = sim.categories['module']
    else:
        module = sim.categories['version']

    return (module, sim.categories['nodes'], ns_day, sim.categories['time'],
            sim.categories['gpu'], sim.categories['host'], ncores)


def write_bench(top, tmpl, nodes, gpu, module, tpr, name, host, time):
    ## TODO: do this centrally somewhere not here! needed in any file
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

    # copy input files
    namd = '{}.namd'.format(name)
    psf = '{}.psf'.format(name)
    pdb = '{}.pdb'.format(name)

    #check whether the basic files are there
    ##TODO: add the namd config file parser here
    ##TODO: the parameters specified in namd must be absolute paths atm! is problem
    for filename in [namd, psf, pdb]:
        if not os.path.exists(filename):
            raise click.FileError(
                filename, hint='File does not exist or is not readable.')

    copyfile(namd, sim[namd].relpath)
    copyfile(psf, sim[psf].relpath)
    copyfile(pdb, sim[pdb].relpath)

    # Add some time buffer to the requested time. Otherwise the queuing system
    # kills the jobs before GROMACS can finish
    formatted_time = '{:02d}:{:02d}:00'.format(*divmod(time + 5, 60))
    # engine switch to pick the right submission statement in the templates
    md_engine = "namd"
    # create bench job script
    script = tmpl.render(
        name=name,
        gpu=gpu,
        module=module,
        formatted_module=md_engine,
        n_nodes=nodes,
        time=time,
        formatted_time=formatted_time)

    with open(sim['bench.job'].relpath, 'w') as fh:
        fh.write(script)


def analyze_namd_file(fh):
    """ Check for parameter files in the namd config file and copy them here
    """

    return 1


def parse_namd_file():
    """
    """
    pass
