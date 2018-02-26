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
import six

from . import gromacs, namd
from .. import console


def detect_md_engine(modulename):
    """Detects the MD engine based on the available modules.
        Any newly implemented mdengines must be added here.
        Returns the python module."""
    _engines = {'gromacs': gromacs, 'namd': namd}

    for name, engine in six.iteritems(_engines):
        if name in modulename:
            return engine

    console.error(
        "No suitable engine detected for '{}'. Known engines are: {}.",
        modulename, ', '.join(sorted(_engines.keys())))
