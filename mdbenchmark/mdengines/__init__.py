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

import six

from . import gromacs, namd
from .. import console

SUPPORTED_ENGINES = {'gromacs': gromacs, 'namd': namd}


def detect_md_engine(modulename):
    """Detects the MD engine based on the available modules.

    Any newly implemented MD engines must be added here.


    Returns
    -------
    The corresponding MD engine module.
    """

    for name, engine in six.iteritems(SUPPORTED_ENGINES):
        if name in modulename:
            return engine

    console.error(
        "There is currently no support for '{}'. Supported MD engines are: {}.",
        modulename, ', '.join(sorted(SUPPORTED_ENGINES.keys())))


def get_available_modules():
    """Return all available module versions for a given MD engine.

    Returns
    -------
    If we cannot access the `MODULEPATH` environment variable, we return None.

    available_modules : dict
        Dictionary containing all available engines as keys and their versions as a list.
    """

    MODULE_PATHS = os.environ.get('MODULEPATH', None)
    available_modules = dict((mdengine, []) for mdengine in SUPPORTED_ENGINES)

    # Return `None` if the environment variable `MODULEPATH` does not exist.
    if not MODULE_PATHS:
        return None

    # Go through the directory structure and grab all version of modules that we support.
    for paths in MODULE_PATHS.split(':'):
        for path, subdirs, files in os.walk(paths):
            for mdengine in SUPPORTED_ENGINES:
                if mdengine in path:
                    for name in files:
                        if not name.startswith('.'):
                            available_modules[mdengine].append(name)

    return available_modules


def validate_module_name(module=None, available_modules=None):
    """Validates that the specified module version is available on the host.

    Returns
    -------
    If `get_available_modules` returns None, so does this function.

    Returns a boolean, indicating whether the specified version is available on the host.
    """
    try:
        basename, version = module.split('/')
    except ValueError:
        console.error('We were not able to determine the module name.')

    if not available_modules:
        available_modules = get_available_modules()

    if available_modules is None:
        return None

    return version in available_modules[basename]
