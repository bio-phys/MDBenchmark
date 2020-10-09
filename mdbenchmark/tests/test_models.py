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

from mdbenchmark.models import Processor


@pytest.mark.parametrize(
    "physical_cores, logical_cores, expected_result", [[80, 40, 80], [40, 40, 40]]
)
def test_get_available_number_of_cores(
    monkeypatch, physical_cores, logical_cores, expected_result
):
    monkeypatch.setattr(
        "mdbenchmark.models.cpu_count",
        lambda logical: logical_cores if logical else physical_cores,
    )
    obj = Processor()
    assert obj._get_number_of_available_cores == expected_result


@pytest.mark.parametrize(
    "physical_cores, logical_cores, number_of_ranks, expected_result",
    [
        [40, 80, 40, True],
        [80, 80, 20, True],
        [40, 40, 80, False],
        [40, 40, 80, False],
        [80, 80, 0, False],
        [80, 80, -1, False],
    ],
)
def test_number_of_ranks_is_valid(
    physical_cores, logical_cores, number_of_ranks, expected_result
):
    obj = Processor(physical_cores, logical_cores)
    assert expected_result == obj.number_of_ranks_is_valid(number_of_ranks)


@pytest.mark.parametrize(
    "physical_cores, logical_cores, expected_result",
    [
        [40, 80, True],
        [40, 40, False],
        [40, 24, False],  # Can the last case ever happen?
    ],
)
def test_supports_hyperthreading(physical_cores, logical_cores, expected_result):
    obj = Processor(physical_cores, logical_cores)
    result = obj.supports_hyperthreading

    assert expected_result == result


@pytest.mark.parametrize(
    "physical_cores, logical_cores, number_of_ranks, with_hyperthreading, expected_result",
    [
        [40, 40, 40, False, (40, 1)],
        [40, 80, 40, True, (40, 2)],
        [40, 80, 40, False, (40, 1)],
        [40, 80, 20, True, (20, 4)],
        [40, 40, 20, False, (20, 2)],
        [40, 40, 4, False, (4, 10)],
        [40, 40, 2, False, (2, 20)],
    ],
)
def test_ranks_and_threads(
    physical_cores, logical_cores, number_of_ranks, with_hyperthreading, expected_result
):
    obj = Processor(physical_cores, logical_cores)
    ranks_threads = obj.get_ranks_and_threads(number_of_ranks, with_hyperthreading)

    assert expected_result == ranks_threads
