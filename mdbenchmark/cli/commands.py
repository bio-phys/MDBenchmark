# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017-2019 The MDBenchmark development team and contributors
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

from .generate import (
    print_known_hosts,
    validate_cpu_gpu_flags,
    validate_hosts,
    validate_module,
    validate_name,
    validate_number_of_nodes,
)
from .options import AliasedGroup


@click.command(cls=AliasedGroup)
@click.version_option()
def cli():
    """Generate, run and analyze benchmarks of molecular dynamics simulations."""
    pass


@cli.command()
def analyze():
    """Analyze docstring."""
    from .analyze import do_analyze

    do_analyze()


@cli.command()
@click.option(
    "-n",
    "--name",
    help="Name of input files. All files must have the same base name.",
    callback=validate_name,
)
@click.option(
    "-c/-nc",
    "--cpu/--no-cpu",
    is_flag=True,
    help="Use CPUs for benchmark.",
    default=True,
    show_default=True,
)
@click.option(
    "-g/-ng",
    "--gpu/--no-gpu",
    is_flag=True,
    help="Use GPUs for benchmark.",
    show_default=True,
)
@click.option(
    "-m",
    "--module",
    help="Name of the MD engine module to use.",
    multiple=True,
    callback=validate_module,
)
@click.option(
    "-t",
    "--template",
    "--host",
    "host",
    help="Name of the host template.",
    default=None,
    callback=validate_hosts,
)
@click.option(
    "--min-nodes",
    help="Minimal number of nodes to request.",
    default=1,
    show_default=True,
    type=int,
)
@click.option(
    "--max-nodes",
    help="Maximal number of nodes to request.",
    default=5,
    show_default=True,
    type=int,
)
@click.option(
    "--time",
    help="Run time for benchmark in minutes.",
    default=15,
    show_default=True,
    type=click.IntRange(1, 1440),
)
@click.option(
    "--list-hosts",
    help="Show available host templates.",
    is_flag=True,
    is_eager=True,
    callback=print_known_hosts,
    expose_value=False,
)
@click.option(
    "--skip-validation",
    help="Skip the validation of module names.",
    default=False,
    is_flag=True,
)
@click.option(
    "--job-name", help="Give an optional to the generated benchmarks.", default=None
)
@click.option(
    "-y", "--yes", help="Answer all prompts with yes.", default=False, is_flag=True
)
def generate(
    name,
    cpu,
    gpu,
    module,
    host,
    min_nodes,
    max_nodes,
    time,
    skip_validation,
    job_name,
    yes,
):
    """Generate benchmarks for molecular dynamics simulations.

    Requires the ``--name`` option to be provided an existing file, e.g.,
    ``protein.tpr`` for GROMACS and ``protein.namd``, ``protein.pdb`` and
    ``protein.psf`` for NAMD. The filename ``protein`` will then be used as the job
    name, or can be overwritten with the ``--job-name`` option.

    The specified module name will be validated and searched on the current
    system. To skip this check, use the ``--skip-validation`` option.

    Benchmarks will be generated for CPUs per default (``--cpu``), but can also
    be generated for GPUs (``--gpu``) at the same time or without CPUs
    (``--no-cpu``).

    The hostname of the current system will be used to look for benchmark
    templates, but can be overwritten with the ``--template`` option. Templates
    for the MPCDF clusters ``cobra``, ``draco`` and ``hydra`` are provided with the
    package. All available templates can be listed with the ``--list-hosts``
    option.
    """
    from .generate import do_generate

    do_generate(
        name=name,
        cpu=cpu,
        gpu=gpu,
        module=module,
        host=host,
        min_nodes=min_nodes,
        max_nodes=max_nodes,
        time=time,
        skip_validation=skip_validation,
        job_name=job_name,
        yes=yes,
    )
