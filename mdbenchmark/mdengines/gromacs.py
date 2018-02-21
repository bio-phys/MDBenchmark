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
from __future__ import absolute_import

import os
import warnings
from glob import glob
from shutil import copyfile

import click
import datreant.core as dtr
import mdsynthesis as mds
import numpy as np
from jinja2.exceptions import TemplateNotFound


def parse_ns_day(fh):
    """parse nanoseconds per day from a GROMACS log file

    Parameters
    ----------
    fh : str / filehandle
        filename or string of log file to read

    Returns
    -------
    float / np.nan
        nanoseconds per day or NaN
    """
    lines = fh.readlines()

    for line in lines:
        if 'Performance' in line:
            return float(line.split()[1])

    return np.nan


def parse_ncores(fh):
    """parse number of cores from a GROMACS log file

    Parameters
    ----------
    fh : str / filehandle
        filename or string of log file to read

    Returns
    -------
    int / np.nan
        number of cores job was run on or NaN
    """
    lines = fh.readlines()

    for line in lines:
        if 'Running on' in line:
            return int(line.split()[6])

    return np.nan


def analyze_run(sim):
    """
    Analyze Performance data of a GROMACS simulation.
    """
    # Set defaults if we are unable to find the information in the log file or
    # the log file does not exist (yet).
    ns_day = np.nan
    ncores = np.nan

    # search all output files and ignore GROMACS backup files
    output_files = glob(os.path.join(sim.relpath, '[!#]*log*'))
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

    copyfile(tpr, sim[tpr].relpath)
    # Add some time buffer to the requested time. Otherwise the queuing system
    # kills the jobs before GROMACS can finish
    formatted_time = '{:02d}:{:02d}:00'.format(*divmod(time + 5, 60))
    md_engine = "gromacs"
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
