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
from psutil import cpu_count


class Processor:
    """Representation of all CPUs of a single node.

    We use the singular "processor", instead of "processors", even if a node has
    multiple CPU sockets.
    """

    def __init__(self, physical_cores=0, logical_cores=0):
        self.physical_cores = physical_cores
        self.logical_cores = logical_cores

        if self.physical_cores == 0 or self.logical_cores == 0:
            self._set_number_of_available_cores()

    def __repr__(self):
        return f"<Processor physical_cores={self.physical_cores}, logical_cores={self.logical_cores}, supports_hyperthreading={self.supports_hyperthreading}>"

    def _set_number_of_available_cores(self):
        """Deterine the number of physical and logical cores with `psutil.cpu_count()`."""
        self.physical_cores = cpu_count(logical=False)
        self.logical_cores = cpu_count(logical=True)

    @property
    def _get_number_of_available_cores(self):
        """Return the number of available cores.

        If hyperthreading is supported, this returns the number of logical cores. In the other case
        it is the number of physical cores."""
        return (
            self.logical_cores if self.supports_hyperthreading else self.physical_cores
        )

    @property
    def supports_hyperthreading(self):
        """Return True if the CPU supports hyperthreading."""
        return self.physical_cores == self.logical_cores // 2

    def number_of_ranks_is_valid(self, number_of_ranks):
        """Validate the input for the number of ranks."""
        # Number of ranks must be equal or bigger than 1.
        if number_of_ranks < 1:
            return False

        remainder = self._get_number_of_available_cores / number_of_ranks

        # The remainder must be equal or bigger than 1.
        if remainder < 1:
            return False

        # All cores are used up by the ranks. This is not a valid setting with
        # hyperthreading.
        if self.supports_hyperthreading and remainder < 2:
            return False

        return True

    def get_ranks_and_threads(self, number_of_ranks, with_hyperthreading=True):
        """Compute the number of OpenMP threads that we can use with number_of_ranks."""
        if not self.number_of_ranks_is_valid(number_of_ranks):
            raise ValueError(
                f"The number of ranks ({number_of_ranks}) is not a valid value on this system!"
            )

        number_of_threads = self._get_number_of_available_cores // number_of_ranks

        if (
            not with_hyperthreading
            and number_of_threads != 1
            and not self.physical_cores == self.logical_cores
        ):
            number_of_threads //= 2

        return (number_of_ranks, number_of_threads)
