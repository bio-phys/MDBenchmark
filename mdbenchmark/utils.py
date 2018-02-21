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
import multiprocessing as mp
import os
import socket
import sys
from glob import glob

import click
import numpy as np
import xdg
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader

import mdengines.gromacs
import mdengines.namd

from .ext.cadishi import _cat_proc_cpuinfo_grep_query_sort_uniq

OUTPUT_FILE_TYPES = ('*.err.*', '*.out.*', '*.log', '*.xtc', '*.cpt', '*.edr',
                     '*.po[1-9]*', '*.o[1-9]*', '*.out')
# Order where to look for host templates: HOME -> etc -> package
# home
_loaders = [
    FileSystemLoader(os.path.join(xdg.XDG_CONFIG_HOME, 'MDBenchmark')),
]
# allow custom folder for templates. Useful for environment modules
_mdbenchmark_env = os.getenv("MDBENCHMARK_TEMPLATES")
if _mdbenchmark_env is not None:
    _loaders.append(FileSystemLoader(_mdbenchmark_env))
# global
_loaders.extend([
    FileSystemLoader(os.path.join(d, 'MDBenchmark'))
    for d in xdg.XDG_CONFIG_DIRS
])
# from package
_loaders.append(PackageLoader('mdbenchmark', 'templates'))
ENV = Environment(loader=ChoiceLoader(_loaders))


def get_possible_hosts():
    return ENV.list_templates()


def print_possible_hosts():
    all_hosts = get_possible_hosts()
    click.echo('Available host templates:')
    for h in all_hosts:
        click.echo('{}'.format(h))


def guess_host():
    hostname = socket.gethostname()
    known_hosts = get_possible_hosts()
    for h in known_hosts:
        if h in hostname:
            return h

    return None


def normalize_host(host):
    if host is None:
        host = guess_host()
        if host is None:
            raise click.BadParameter(
                'Could not guess host. Please provide a value explicitly.',
                param_hint='"--host"')
    return host


def lin_func(x, m, b):
    return m * x + b


def calc_slope_intercept(x1, y1, x2, y2):
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - (x1 * slope)

    return np.hstack([slope, intercept])


def cleanup_before_restart(sim):
    files_found = []
    for t in OUTPUT_FILE_TYPES:
        try:
            p = sim.path.__str__()
        except AttributeError:
            p = str(sim)
        files_found.extend(glob(os.path.join(p, t)))

    for f in files_found:
        os.remove(f)


def guess_ncores():
    """Guess the number of physical CPU cores.

    We inspect `/proc/cpuinfo` to grab the actual number."""
    total_cores = None
    if sys.platform.startswith('linux'):
        nsocket = len(_cat_proc_cpuinfo_grep_query_sort_uniq('physical id'))
        ncores = len(_cat_proc_cpuinfo_grep_query_sort_uniq('core id'))
        total_cores = ncores * nsocket
    elif sys.platform == 'darwin':
        # assumes we have an INTEL CPU with hyper-threading. As of 2017 this is
        # true for all officially supported Apple models.
        total_cores = mp.cpu_count() // 2
    if total_cores is None:
        click.echo('{} Could not guess number of physical cores. '
                   'Assuming there is only 1 core per node.'.format(
                       click.style('WARNING', fg='yellow', bold=True)))
        total_cores = 1
    return total_cores

#detects the module names and returns the package
def detect_md_engine(modulename):
    """Detects the MD engine based on the available modules.
        Any newly implemeted mdengines must be added here.
    """
    if 'gromacs' in modulename:
        print(modulename)
        return mdengines.gromacs
    elif 'namd' in modulename:
        return mdengines.namd
    else:
        raise RuntimeError("No Module Detected! did you specify the module?")

def formatted_md_engine_name(modulename):
    if 'gromacs' in modulename:
        return "gromacs"
    elif 'namd' in modulename:
        return "namd"
    else:
        raise RuntimeError("No Module Detected! did you specify the module?")
