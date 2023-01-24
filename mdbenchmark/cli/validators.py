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
import click
import numpy as np

from mdbenchmark import console, utils


def validate_cores(ctx, param, *args, **kwargs):
    """Validate that we are given a positive integer bigger than 0."""
    for option, value in kwargs.items():
        if value is None or not isinstance(int, value) or value < 1:
            raise click.BadParameter(
                "Please specify the number of {option} cores.".format(option=option),
                param_hint='"--{option}"',
            )


def validate_name(ctx, param, name=None):
    """Validate that we are given a name argument."""
    if name is None:
        raise click.BadParameter(
            "Please specify the base name of your input files.",
            param_hint='"-n" / "--name"',
        )

    return name


def validate_module(ctx, param, module=None):
    """Validate that we are given a module argument."""
    if module is None or not module:
        raise click.BadParameter(
            "Please specify which MD engine module to use for the benchmarks.",
            param_hint='"-m" / "--module"',
        )
    return module


def validate_cpu_gpu_flags(cpu, gpu):
    """Validate that either the CPU or GPU flag is set to True."""
    if not (cpu or gpu):
        raise click.BadParameter(
            "You must select either CPUs or GPUs to run the benchmarks on.",
            param_hint='"--cpu" / "--gpu"',
        )


def validate_number_of_nodes(min_nodes, max_nodes):
    """Validate that the minimal number of nodes is smaller than the maximal
    number.
    """
    if min_nodes > max_nodes:
        raise click.BadParameter(
            "The minimal number of nodes needs to be smaller than the maximal number.",
            param_hint='"--min-nodes"',
        )


def validate_number_of_simulations(nsims, min_nodes, max_nodes, nranks):
    """validate that the number of simulations is an integer multiple of
    number of nodes times number of ranks per node.
    """
    for nn in range(min_nodes, max_nodes + 1):
        nranks = np.array([nn * ri for ri in nranks])
        for nsim in nsims:
            if np.any(nranks % nsim):
                raise click.BadParameter(
                    "The total number of ranks must be an integer multiple of"
                    + " the number of simulations",
                    param_hint='"--multidir" / "--ranks" / "--min-nodes" / "--max-nodes"',
                )


def print_known_hosts(ctx, param, value):
    """Callback to print all available hosts to the user."""
    if not value or ctx.resilient_parsing:
        return
    utils.print_possible_hosts()
    ctx.exit()


def validate_hosts(ctx, param, host=None):
    """Callback to validate the hostname received as input.

    If we were not given a hostname, we first try to guess it via
    `utils.guess_host`. If this fails, we give up and throw an error.

    Otherwise we compare the provided/guessed host with the list of available
    templates. If the hostname matches the template name, we continue by
    returning the hostname.
    """
    if host is None:
        host = utils.guess_host()
        if host is None:
            raise click.BadParameter(
                "Could not guess host. Please provide a value explicitly.",
                param_hint='"--host"',
            )

    known_hosts = utils.get_possible_hosts()
    if host not in known_hosts:
        console.info("Could not find template for host '{}'.", host)
        utils.print_possible_hosts()
        # TODO: Raise some appropriate error here
        ctx.exit()
        return

    return host
