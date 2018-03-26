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
import datetime as dt
import multiprocessing as mp
import os
import socket
import sys

import click
import numpy as np
import xdg
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader
from jinja2.exceptions import TemplateNotFound

from . import console
from .ext.cadishi import _cat_proc_cpuinfo_grep_query_sort_uniq

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
    console.info('Available host templates:')
    for host in all_hosts:
        console.info(host)


def guess_host():
    hostname = socket.gethostname()
    known_hosts = get_possible_hosts()
    for host in known_hosts:
        if host in hostname:
            return host

    return None


def retrieve_host_template(host=None):
    """Lookup the template name.

    Parameter
    ---------
    host : str
      Name of the host template to lookup

    Returns
    -------
    template
    """
    return ENV.get_template(host)


def lin_func(x, m, b):
    return m * x + b


def calc_slope_intercept(x1, y1, x2, y2):
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - (x1 * slope)

    return np.hstack([slope, intercept])


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
        console.warn('Could not guess number of physical cores. '
                     'Assuming there is only 1 core per node.')
        total_cores = 1
    return total_cores


def generate_output_name(extension):
    """ generate a unique filename based on the date and time for a given extension.
    """
    date_time = dt.datetime.now().strftime("%m%d%y_%H-%M")
    out = '{}.{}'.format(date_time, extension)
    return out
