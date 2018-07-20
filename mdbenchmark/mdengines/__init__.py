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

    The corresponding MD engine module or `None` if the requested module is not
    supported.
    """

    for name, engine in six.iteritems(SUPPORTED_ENGINES):
        if name in modulename.lower():
            return engine

    return None


def prepare_module_name(module, skip_validation=False):
    """Split the provided module name into its base MD engine and version.

    Currently we only try to split via the delimiter `/`, but this could be
    changed upon request or made configurable on a per-host basis.
    """
    try:
        basename, version = module.split('/')
    except (ValueError, AttributeError) as e:
        if skip_validation:
            console.error('Although you are using the {} option, you have to provide a valid '
                          'MD engine name, e.g., {} or {}.',
                          '--skip-validation', 'gromacs/dummy', 'namd/dummy')
        console.error('We were not able to determine the module name.')

    return basename, version


def get_available_modules():
    """Return all available module versions for a given MD engine.

    Returns
    -------
    If we cannot access the `MODULEPATH` environment variable, we return `None`.

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


def normalize_modules(modules, skip_validation):
    """Validate that the provided module names are available.

    We first check whether the requested MD engine is supported by the package.
    Next we try to discover all available modules on the host. If this is not
    possible, or if the user has used the `--skip-validation` option, we skip
    the check and notify the user.

    If the user requested modules that were not found on the system, we inform
    the user and show all modules for that corresponding MD engine that were
    found.
    """
    # Check if modules are from supported md engines
    d = defaultdict(list)
    for m in modules:
        engine_name, version = prepare_module_name(m, skip_validation)
        d[engine_name] = version
    for engine_name in d.keys():
        if detect_md_engine(engine_name) is None:
            console.error("There is currently no support for '{}'. "
                          "Supported MD engines are: gromacs, namd.",
                          engine_name)

    if skip_validation:
        console.warn('Not performing module name validation.')
        return modules

    available_modules = get_available_modules()
    if available_modules is None:
        console.warn(
            'Cannot locate modules available on this host. Not performing module name validation.'
        )
        return modules

    good_modules = [
        m for m in modules if validate_module_name(m, available_modules)
    ]

    # Prepare to warn the user about missing modules
    missing_modules = set(modules).difference(good_modules)
    if missing_modules:
        d = defaultdict(list)
        for mm in sorted(missing_modules):
            engine_name, version = mm.split('/')
            d[engine_name].append(version)

        err = 'We have problems finding all of your requested modules on this host.\n'
        args = []
        for engine_name in sorted(d.keys()):
            err += 'We were not able to find the following modules for MD engine {}: {}.\n'
            args.append(engine_name)
            args.extend(d[engine_name])
            # Show all available modules that we found for the requested MD engine
            err += 'Available modules are:\n{}\n'
            args.extend([
                '\n'.join([
                    '{}/{}'.format(engine_name, mde)
                    for mde in sorted(available_modules[engine_name])
                ])
            ])
        console.warn(err, bold=True, *args)

    return good_modules


def validate_module_name(module, available_modules=None):
    """Validates that the specified module version is available on the host.

    Returns
    -------

    Returns True or False, indicating whether the specified version is
    available on the host.
    """
    basename, version = prepare_module_name(module)

    return version in available_modules[basename]
