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
import os
import uuid

import datreant as dtr
import pytest

from mdbenchmark.migrations import mds_to_dtr


def test_ensure_correct_environment(capsys, monkeypatch):
    # A working environment should not yield any errors
    mds_to_dtr.ensure_correct_environment()

    # Mock an installed `datreant<1.0`
    monkeypatch.delattr("datreant.__version__")
    with pytest.raises(SystemExit):
        mds_to_dtr.ensure_correct_environment()
        out, err = capsys.readouterr()

        assert out == mds_to_dtr.MIGRATION_WARNING.format("datreant.core")


def create_file(bundle, path, filename):
    data = {
        "mdsynthesis": {},
        "categories": {
            "name": "bench",
            "started": "true",
            "module": "gromacs/2016.3",
            "host": "draco",
            "time": 15,
            "gpu": "false",
            "nodes": 1,
        },
        "tags": [],
    }

    file = bundle.join(filename)
    data = str(data).replace("'", '"')
    file.write(str(data))

    return str(file)


@pytest.fixture
def create_sim_files(tmpdir):
    sim_files = []
    directory = tmpdir.mkdir("draco_gromacs").mkdir("2018.1")
    for path in ["1", "2", "3"]:
        bundle = directory.mkdir(path)
        filename = "Sim.{uid}.json".format(uid=uuid.uuid4())
        sim = create_file(bundle, path, filename)
        sim_files.append(sim)

        proxy_filename = ".{filename}.proxy".format(filename=filename)
        proxy = create_file(bundle, path, proxy_filename)
        sim_files.append(proxy)

        tpr = create_file(bundle, path, "md.tpr")
        sim_files.append(tpr)

    return directory, sim_files


def test_search_mdsynthesis_sim_files(create_sim_files):
    directory, files = create_sim_files

    bundles = mds_to_dtr.search_mdsynthesis_sim_files(str(directory))
    files = [file for file in files if file.endswith(".json")]
    assert sorted(bundles) == sorted(files)


def test_convert_to_datreant(create_sim_files):
    directory, files = create_sim_files

    sim_files = [file for file in files if file.endswith(".json")]
    proxy_files = [file for file in files if file.endswith(".proxy")]
    files_to_keep = [file for file in files if ".json" not in file]
    mds_to_dtr.convert_to_datreant(sim_files)

    for path in ["1", "2", "3"]:
        # New directory and files exist
        treant = os.path.join(str(directory), path, ".datreant")
        assert os.path.exists(os.path.join(treant))
        assert os.path.exists(os.path.join(treant, "categories.json"))

    # Old files were deleted correctly, others were kept
    for file in proxy_files:
        assert not os.path.exists(file)
    for file in files_to_keep:
        assert os.path.exists(file)


def test_migrate_to_datreant(tmpdir, capsys, create_sim_files):
    directory, files = create_sim_files

    with tmpdir.as_cwd():
        assert mds_to_dtr.migrate_to_datreant(".") is None

    mds_to_dtr.migrate_to_datreant(str(directory))
    out, err = capsys.readouterr()

    output = (
        "Converting old benchmark metadata to new format!\n"
        "Finished converting old benchmarks to new format!\n"
    )

    assert out == output
