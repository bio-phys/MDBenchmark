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
from six import string_types
import warnings


def parse_ns_day(fh):
    """parse nanoseconds per day from a GROMACS log file

    Parameters
    ----------
    fh : str / filehandle
        filename or string of log file to read

    Returns
    -------
    float
        nanoseconds per day
    """

    if isinstance(fh, string_types):
        with open(fh) as f:
            lines = f.readlines()
    else:
        lines = fh.readlines()
        fh.seek(0)

    for line in lines:
        if 'Performance' in line:
            return float(line.split()[1])
    warnings.warn(UserWarning, "No Performance data found.")
    return 0


def analyze_run(sim):
    """
    Analyze Performance data of a GROMACS simulation
    """
    ns_day = 0

    # search all output files and ignore GROMACS backup files
    output_files = glob(os.path.join(sim.relpath, '[!#]*log*'))
    if output_files:
        with open(output_files[0]) as fh:
            ns_day = parse_ns_day(fh)

    # Backward compatibility to previously created mdbenchmark systems
    if 'time' not in sim.categories:
        sim.categories['time'] = 0

    # backward compatibility
    if 'module' in sim.categories:
        module = sim.categories['module']
    else:
        module = sim.categories['version']

    return (module, sim.categories['nodes'], ns_day, sim.categories['time'],
            sim.categories['gpu'], sim.categories['host'])
