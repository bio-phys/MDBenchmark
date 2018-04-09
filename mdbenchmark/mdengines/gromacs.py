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
import re
from glob import glob
from shutil import copyfile

import mdsynthesis as mds
import numpy as np

from .. import console

NAME = 'gromacs'




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

    # Backward compatibility to previously created benchmark systems
    if 'time' not in sim.categories:
        sim.categories['time'] = 0

    # backward compatibility
    if 'module' in sim.categories:
        module = sim.categories['module']
    else:
        module = sim.categories['version']

    return (module, sim.categories['nodes'], ns_day, sim.categories['time'],
            sim.categories['gpu'], sim.categories['host'], ncores)


def check_input_file_exists(name):
    """Check if the TPR file exists.
    """
    fn = name
    if fn.endswith('.tpr'):
        fn = name[:-4]

    tpr = fn + '.tpr'
    if not os.path.exists(tpr):
        console.error(
            "File {} does not exist, but is needed for GROMACS benchmarks.",
            tpr)

    return
