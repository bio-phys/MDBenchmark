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
import datreant.core as dtr
from jinja2.exceptions import TemplateNotFound

from . import console
from .cli import cli
from .mdengines import detect_md_engine, namd
from .utils import ENV, normalize_host, print_possible_hosts


@cli.command()
@click.option(
    '-n',
    '--name',
    help='Name of input files. All files must have the same base name.',
    show_default=True)
@click.option(
    '-g',
    '--gpu',
    is_flag=True,
    help='Use GPUs for benchmark.',
    show_default=True)
@click.option(
    '-m',
    '--module',
    help='Name of the MD engine module to use.',
    multiple=True)
@click.option('--host', help='Name of the job template.', default=None)
@click.option(
    '--min-nodes',
    help='Minimal number of nodes to request.',
    default=1,
    show_default=True,
    type=int)
@click.option(
    '--max-nodes',
    help='Maximal number of nodes to request.',
    default=5,
    show_default=True,
    type=int)
@click.option(
    '--time',
    help='Run time for benchmark in minutes.',
    default=15,
    show_default=True,
    type=click.IntRange(1, 1440))
@click.option(
    '--list-hosts', help='Show available job templates.', is_flag=True)
def generate(name, gpu, module, host, min_nodes, max_nodes, time, list_hosts):
    """Generate benchmarks."""
    if list_hosts:
        print_possible_hosts()
        return

    if not name:
        raise click.BadParameter(
            'Please specify the base name of your input files.',
            param_hint='"-n" / "--name"')

    if not module:
        raise click.BadParameter(
            'Please specify which mdengine module to use for the benchmarks.',
            param_hint='"-m" / "--module"')

    if min_nodes > max_nodes:
        raise click.BadParameter(
            'The minimal number of nodes needs to be smaller than the maximal number.',
            param_hint='"--min-nodes"')

    host = normalize_host(host)
    try:
        tmpl = ENV.get_template(host)
    except TemplateNotFound:
        raise click.BadParameter(
            'Could not find template for host \'{}\'.'.format(host),
            param_hint='"--host"')

    # Make sure we only warn the user once, if they are using NAMD.
    if any(['namd' in m for m in module]):
        console.warn(
            'NAMD support is experimental. '
            'All input files must be in the current directory. '
            'Parameter paths must be absolute. Only crude file checks are performed!'
            'If you use the {} option make sure you use the GPU compatible NAMD module!',
            '--gpu')

    for m in module:
        # Here we detect the mdengine (GROMACS or NAMD).
        engine = detect_md_engine(m)

        directory = '{}_{}'.format(host, m)
        gpu_string = ''
        if gpu:
            directory += '_gpu'
            gpu_string = ' with GPUs'

        # Check if all needed files exist. Throw an error if they do not.
        engine.check_input_file_exists(name)

        console.info('Creating benchmark system for {}.', m + gpu_string)
        number_of_benchmarks = (len(module) * (max_nodes + 1 - min_nodes))
        run_time_each = '{} minutes'.format(time)
        console.info(
            'Creating a total of {} benchmarks, with a run time of {} each.',
            number_of_benchmarks, run_time_each)

        top = dtr.Tree(directory)
        for n in range(min_nodes, max_nodes + 1):
            engine.write_bench(
                top=top,
                tmpl=tmpl,
                nodes=n,
                gpu=gpu,
                module=m,
                name=name,
                host=host,
                time=time)

    # Provide some output for the user
    console.info('Finished generating all benchmarks.\n'
                 'You can now submit the jobs with {}.', 'mdbenchmark submit')
