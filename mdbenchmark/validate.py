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
import click

from .utils import ENV, normalize_host


def validate_generate_name(name=None):
    """Validate that we are given a name argument."""
    if not name:
        raise click.BadParameter(
            'Please specify the base name of your input files.',
            param_hint='"-n" / "--name"')


def validate_generate_module(module=None):
    """Validate that we are given a module argument."""
    if not module:
        raise click.BadParameter(
            'Please specify which MD engine module to use for the benchmarks.',
            param_hint='"-m" / "--module"')


def validate_generate_number_of_nodes(min_nodes, max_nodes):
    """Validate that the minimal number of nodes is not smaller than the maximal number."""
    if min_nodes > max_nodes:
        raise click.BadParameter(
            'The minimal number of nodes needs to be smaller than the maximal number.',
            param_hint='"--min-nodes"')


def validate_generate_host(host=None):
    """Validate that we were given a valid template name for the host."""
    if not host:
        raise click.BadParameter(
            'Could not find template for host \'{}\'.'.format(host),
            param_hint='"--host"')


def validate_generate_arguments(name=None,
                                module=None,
                                host=None,
                                min_nodes=None,
                                max_nodes=None):
    """Validate all input provided to the generate CLI command."""
    validate_generate_name(name=name)
    validate_generate_module(module=module)
    validate_generate_host(host=host)
    validate_generate_number_of_nodes(min_nodes=min_nodes, max_nodes=max_nodes)
