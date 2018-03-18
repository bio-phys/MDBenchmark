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
from collections import defaultdict

import six

from . import gromacs, namd
from .. import console

SUPPORTED_ENGINES = {'gromacs': gromacs, 'namd': namd}


def detect_md_engine(modulename):
    """Detects the MD engine based on the available modules.

    Any newly implemented MD engines must be added here.


    Returns
    -------
    The corresponding MD engine module or None if the requested module is not supported.
    """

    for name, engine in six.iteritems(SUPPORTED_ENGINES):
        if name in modulename:
            return engine

    return None


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


def normalize_modules(modules):
    # Check if modules are from supported md engines
    d = defaultdict(list)
    for m in modules:
        engine, version = m.split('/')
        d[engine] = version
    for engine in d.keys():
        if detect_md_engine(engine) is None:
            console.warn("There is currently no support for '{}'", engine)

    available_modules = get_available_modules()
    if available_modules is None:
        console.warn('Cannot locate modules available on this host.')
        return modules

    good_modules = [
        m for m in modules if validate_module_name(m, available_modules)
    ]

    # warn about missing modules
    missing_modules = set(good_modules).difference(modules)
    if missing_modules:
        d = defaultdict(list)
        for mm in missing_modules:
            engine, version = mm.split('/')
            d[engine].append(version)

        err = 'We have problems finding all of your requested modules on this host.\n'
        args = []
        for engine in sorted(d.keys()):
            err += 'We were not able to find the following modules for MD engine {}: {}.\n'
            args.append(engine)
            args.extend(d[engine])
            # If we know the MD engine that the user was trying to use, we can
            # show all available options.
            err += 'Available modules are:\n{}\n'
            args.extend([
                '\n'.join([
                    '{}/{}'.format(engine, mde)
                    for mde in available_modules[engine]
                ])
            ])
        console.warn(err, bold=True, *args)

    return good_modules


def validate_module_name(module, available_modules):
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
    return version in available_modules[basename]
