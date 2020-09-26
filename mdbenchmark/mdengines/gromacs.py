# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017-2020 The MDBenchmark development team and contributors
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
import string
from shutil import copyfile

from mdbenchmark import console

NAME = "gromacs"

LOWERCASE_LETTERS = string.ascii_lowercase


def prepare_benchmark(name, relative_path, *args, **kwargs):
    benchmark = kwargs["benchmark"]

    full_filename = name + ".tpr"
    if name.endswith(".tpr"):
        full_filename = name
        name = name[:-4]

    filepath = os.path.join(relative_path, full_filename)

    if kwargs["multidir"] == 1:
        copyfile(filepath, benchmark[full_filename].relpath)
    else:
        for i in range(kwargs["multidir"]):
            subdir = benchmark[LOWERCASE_LETTERS[i] + "/" + full_filename].make()
            copyfile(filepath, subdir.relpath)

    return name


def prepare_multidir(multidir):
    multidir_string = ""

    if multidir != 1:
        multidir_string = "-multidir"
        for i in range(multidir):
            multidir_string += " " + LOWERCASE_LETTERS[i]

    return multidir_string


def check_input_file_exists(name):
    """Check if the TPR file exists."""
    fn = name
    if fn.endswith(".tpr"):
        fn = name[:-4]

    tpr = fn + ".tpr"
    if not os.path.exists(tpr):
        console.error(
            "File {} does not exist, but is needed for GROMACS benchmarks.", tpr
        )

    return True
