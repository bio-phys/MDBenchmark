# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017-2018 The MDBenchmark development team and contributors
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
from six.moves import StringIO

import datreant as dtr
import numpy as np
import pytest

from mdbenchmark.mdengines import gromacs, utils


@pytest.fixture
def log():
    return StringIO(
        """
    Performance:           123.45           0.123
    Running on 1 node with total 32 cores, 64 logical cores, 0 compatible GPUs
    """
    )


@pytest.fixture
def empty_log():
    return StringIO(
        """
    not the log you are looking for
    """
    )


def test_parse_ns_day(log):
    assert utils.parse_ns_day(gromacs, log) == 123.45


def test_parse_ncores(log):
    assert utils.parse_ncores(gromacs, log) == 32


@pytest.mark.parametrize("parse", (utils.parse_ncores, utils.parse_ns_day))
def test_parse_empty_log(empty_log, parse):
    assert np.isnan(parse(gromacs, empty_log))


@pytest.fixture
def sim(tmpdir_factory):
    folder = tmpdir_factory.mktemp("simulation")
    return dtr.Treant(
        str(folder),
        categories={
            "nodes": 42,
            "host": "draco",
            "gpu": False,
            "module": "gromacs/5.1.4",
        },
    )


@pytest.fixture
def sim_old(tmpdir_factory):
    folder = tmpdir_factory.mktemp("simulation")
    return dtr.Treant(
        str(folder),
        categories={"nodes": 42, "host": "draco", "gpu": False, "version": "5.1.4"},
    )


def test_analyze_run(sim):
    res = utils.analyze_run(gromacs, sim)
    assert res[0] == "gromacs/5.1.4"  # version
    assert res[1] == 42  # nodes
    assert np.isnan(res[2])  # ns_day
    assert res[3] == 0  # time
    assert not res[4]  # gpu
    assert res[5] == "draco"  # host
    assert np.isnan(res[6])  # ncores


def test_analyze_run_backward_compatibility(sim_old):
    res = utils.analyze_run(gromacs, sim_old)
    assert res[0] == "5.1.4"  # version
    assert res[1] == 42  # nodes
    assert np.isnan(res[2])  # ns_day
    assert res[3] == 0  # time
    assert not res[4]  # gpu
    assert res[5] == "draco"  # host
    assert np.isnan(res[6])  # ncores


@pytest.mark.parametrize("input_name", ["md", "md.tpr"])
def test_check_file_extension(capsys, input_name, tmpdir):
    """Test that we check for all files needed to run GROMACS benchmarks."""
    output = "ERROR File md.tpr does not exist, but is needed for GROMACS benchmarks.\n"
    with pytest.raises(SystemExit) as e:
        gromacs.check_input_file_exists(input_name)
        out, err = capsys.readouterr()
        assert e.type == SystemExit
        assert e.code == 1
        assert out == output

    with tmpdir.as_cwd():
        # Create files first
        with open("md.tpr", "w") as fh:
            fh.write("dummy file")

        assert gromacs.check_input_file_exists(input_name)
