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
import os
from shutil import copyfile

import click
import datreant.core as dtr
import mdsynthesis as mds
from jinja2.exceptions import TemplateNotFound

from .cli import cli
from .utils import ENV, normalize_host, print_possible_hosts


def write_bench(top, tmpl, nodes, gpu, module, tpr, name, host, time):
    sim = mds.Sim(
        top['{}/'.format(nodes)],
        categories={
            'module': module,
            'gpu': gpu,
            'nodes': nodes,
            'host': host,
            'time': time,
            'name': name,
            'started': False
        })

    copyfile(tpr, sim[tpr].relpath)

    # Add some time buffer to the requested time. Otherwise the queuing system
    # kills the jobs before GROMACS can finish
    formatted_time = '{:02d}:{:02d}:00'.format(*divmod(time + 5, 60))

    # create bench job script
    script = tmpl.render(
        name=name,
        gpu=gpu,
        module=module,
        n_nodes=nodes,
        time=time,
        formatted_time=formatted_time)

    with open(sim['bench.job'].relpath, 'w') as fh:
        fh.write(script)


@cli.command()
@click.option(
    '-n', '--name', help='Name of .tpr file.', default='md', show_default=True)
@click.option(
    '-g',
    '--gpu',
    is_flag=True,
    help='Use GPUs for benchmark.',
    show_default=True)
@click.option('-m', '--module', help='GROMACS module to use.', multiple=True)
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

    # Check that the .tpr file exists.
    fn, ext = os.path.splitext(name)

    if not ext:
        ext = '.tpr'

    tpr = fn + ext
    if not os.path.exists(tpr):
        raise click.FileError(
            tpr, hint='File does not exist or is not readable.')

    host = normalize_host(host)
    try:
        tmpl = ENV.get_template(host)
    except TemplateNotFound:
        raise click.BadParameter(
            'Could not find template for host \'{}\'.'.format(host),
            param_hint='"--host"')

    if not module:
        raise click.BadParameter(
            'You did not specify which gromacs module to use for scaling.',
            param_hint='"-m" / "--module"')

    # Provide some output for the user
    number_of_mdbenchmarks = click.style(
        '{}'.format(len(module) * max_nodes), bold=True)
    run_time_each = click.style('{} minutes'.format(time), bold=True)
    click.echo(
        'Creating a total of {} benchmarks, with a run time of {} each.'.
        format(number_of_mdbenchmarks, run_time_each))

    for m in module:
        directory = '{}_{}'.format(host, m)
        gpu_string = '.'

        if gpu:
            directory += '_gpu'
            gpu_string = ' with GPUs.'
        top = dtr.Tree(directory)

        # More user output
        gromacs_module = click.style('{}'.format(m), bold=True)
        click.echo('Creating benchmark system for {}{}'.format(
            gromacs_module, gpu_string))

        for n in range(min_nodes, max_nodes + 1):
            write_bench(top, tmpl, n, gpu, m, tpr, name, host, time)

    click.echo('Finished generating all benchmarks.')
    click.echo('You can now submit the jobs with {}.'.format(
        click.style('mdbenchmark submit', bold=True)))
