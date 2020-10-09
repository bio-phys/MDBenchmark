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
# along with MDBenchmark.  If not, see <http://www.gnu.org/licenses/>
import pytest

from mdbenchmark.versions import VersionCategories, VersionFactory

CATEGORIES = {
    "VERSION_2": ["name", "started", "module", "host", "time", "gpu", "nodes"],
    "VERSION_3": [
        "name",
        "started",
        "module",
        "host",
        "time",
        "gpu",
        "nodes",
        "version",
    ],
}

IMPLEMENTED_VERSION_CLASSES = [cls for cls in VersionCategories.__subclasses__()]


def test_init_raises_exception():
    with pytest.raises(ValueError) as err:
        VersionFactory()

    assert "must be set" in str(err.value)


@pytest.mark.parametrize("version", ("2", "3"))
def test_version(version):
    obj = VersionFactory(version=version)
    assert obj.version == version


@pytest.mark.parametrize("version", ("2", "3"))
def test_guess_version(version):
    obj = VersionFactory(categories=CATEGORIES[f"VERSION_{version}"])
    assert obj.version == version


def test_version_class_zero_does_not_exist():
    obj = VersionFactory(version="0")
    assert obj.version_class is None


@pytest.mark.parametrize(
    "attribute",
    (
        "version",
        "consolidate_categories",
        "generate_categories",
        "generate_mapping",
        "generate_printing",
        "analyze_categories",
        "analyze_printing",
        "analyze_sort",
        "category_mapping",
    ),
)
def test_not_implemented(attribute):
    obj = VersionCategories()
    assert getattr(obj, attribute) == NotImplemented
