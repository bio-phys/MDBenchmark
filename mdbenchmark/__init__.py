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
import warnings

# Get rid of the h5py FutureWarning
with warnings.catch_warnings():
    warnings.filterwarnings(
        message='.*Conversion of the second.*',
        action='ignore',
        category=FutureWarning,
        module='h5py')

    warnings.filterwarnings(
        message='.*No module named \'duecredit\'.*',
        action='ignore',
        category=UserWarning,
        module='MDAnalysis')

    from . import analyze, generate, submit

    __version__ = '1.3.3'
