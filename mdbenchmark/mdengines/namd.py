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

NAME = 'namd'


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
