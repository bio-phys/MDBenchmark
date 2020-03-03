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

from mdbenchmark.cli.options import AliasedGroup
from mdbenchmark.cli.validators import (
    print_known_hosts,
    validate_cpu_gpu_flags,
    validate_hosts,
    validate_module,
    validate_name,
    validate_number_of_nodes,
)
from mdbenchmark.version import VERSION


@click.group(cls=AliasedGroup)
@click.version_option(version=VERSION)
def cli():
    """Generate, run and analyze benchmarks of molecular dynamics simulations."""
    pass


@cli.command()
@click.option(
    "-d",
    "--directory",
    help="Path in which to look for benchmarks.",
    default=".",
    show_default=True,
)
@click.option(
    "-p",
    "--plot",
    is_flag=True,
    help="DEPRECATED. Please use 'mdbenchmark plot'.\nGenerate a plot of finished benchmarks.",
)
@click.option(
    "--ncores",
    "--number-cores",
    "ncores",
    type=int,
    default=None,
    help="DEPRECATED. Please use 'mdbenchmark plot'.\nNumber of cores per node. If not given it will be parsed from the benchmarks' log file.",
    show_default=True,
)
@click.option(
    "-s",
    "--save-csv",
    default=None,
    help="Filename for the CSV file containing benchmark results.",
)
def analyze(directory, plot, ncores, save_csv):
    """Analyze benchmarks and print the performance results.

    Benchmarks are searched recursively starting from the directory specified
    in ``--directory``. If the option is not specified, the working directory
    will be used.

    Benchmarks that have not started yet or finished without printing the
    performance result, will be marked accordingly.

    The benchmark performance results can be saved in a CSV file with the
    ``--save-csv`` option and a custom filename. To plot the results use
    ``mdbenchmark plot``.
    """
    from mdbenchmark.cli.analyze import do_analyze

    do_analyze(directory=directory, plot=plot, ncores=ncores, save_csv=save_csv)


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
    from mdbenchmark.cli.generate import do_generate

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


@cli.command()
@click.option("--csv", help="Name of CSV file to plot.", multiple=True)
@click.option("-o", "--output-name", help="Filename for the generated plot.")
@click.option(
    "-f",
    "--output-format",
    help="File format for the generated plot.",
    type=click.Choice(["png", "pdf", "svg", "ps"]),
    show_default=True,
    default="png",
)
@click.option(
    "-m",
    "--module",
    "module",
    multiple=True,
    help="Name of the MD engine module(s) to plot.",
)
@click.option(
    "-t",
    "--template",
    "--host",
    "template",
    multiple=True,
    help="Name of host templates to plot.",
)
@click.option(
    "-g/-ng",
    "--gpu/--no-gpu",
    help="Plot data of GPU benchmarks.",
    show_default=True,
    default=True,
)
@click.option(
    "-c/-nc",
    "--cpu/--no-cpu",
    help="Plot data of CPU benchmarks.",
    show_default=True,
    default=True,
)
@click.option(
    "--plot-cores",
    help="Plot performance per core instead performance per node.",
    show_default=True,
    is_flag=True,
)
@click.option(
    "--fit/--no-fit",
    help="Fit a line through the first two data points, indicating linear scaling.",
    show_default=True,
    default=True,
)
@click.option(
    "--font-size", help="Font size for generated plot.", default=16, show_default=True
)
@click.option(
    "--dpi",
    help="Dots per inch (DPI) for generated plot.",
    default=300,
    show_default=True,
)
@click.option(
    "--xtick-step", help="Override the step for xticks in the generated plot.", type=int
)
@click.option(
    "--watermark/--no-watermark",
    help="Puts a watermark in the top left corner of the generated plot.",
    default=True,
    show_default=True,
    is_flag=True,
)
def plot(
    csv,
    output_name,
    output_format,
    template,
    module,
    gpu,
    cpu,
    plot_cores,
    fit,
    font_size,
    dpi,
    xtick_step,
    watermark,
):
    """Generate plots showing the benchmark performance.

    To generate a plot, you must first run ``mdbenchmark analyze`` and generate a
    CSV file. Use this CSV file as the value for the ``--csv`` option in this
    command.

    You can customize the filename and file format of the generated plot with
    the ``--output-name`` and ``--output-format`` option, respectively. Per default, a fit
    will be plotted through the first data points of each benchmark group. To
    disable the fit, use the ``--no-fit`` option.

    To only plot specific benchmarks, make use of the ``--module``, ``--template``,
    ``--cpu/--no-cpu`` and ``--gpu/--no-gpu`` options.

    A small watermark will be added to the top left corner of every plot, to
    spread the usage of MDBenchmark. You can remove the watermark with the
    ``--no-watermark`` option.
    """
    from mdbenchmark.cli.plot import do_plot

    do_plot(
        csv,
        output_name,
        output_format,
        template,
        module,
        gpu,
        cpu,
        plot_cores,
        fit,
        font_size,
        dpi,
        xtick_step,
        watermark,
    )


@cli.command()
@click.option(
    "-d",
    "--directory",
    help="Path in which to look for benchmarks.",
    default=".",
    show_default=True,
)
@click.option(
    "-f",
    "--force",
    "force_restart",
    help="Resubmit all benchmarks and delete all previous results.",
    is_flag=True,
)
@click.option("-y", "--yes", is_flag=True, help="Answer all prompts with yes.")
def submit(directory, force_restart, yes):
    """Submit benchmarks to queuing system.

    Benchmarks are searched recursively starting from the directory specified
    in ``--directory``. If the option is not specified, the working directory
    will be used.

    Requests a user prompt. Using ``--yes`` flag skips this step.

    Checks whether benchmark folders were already generated, exits otherwise.
    Only runs benchmarks that were not already started. Can be overwritten with
    ``--force``.
    """
    from mdbenchmark.cli.submit import do_submit

    do_submit(directory=directory, force_restart=force_restart, yes=yes)
