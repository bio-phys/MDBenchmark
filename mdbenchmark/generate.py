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

from . import console
from .cli import cli
from . import utils
from . import mdengines


def validate_name(ctx, param, name=None):
    """Validate that we are given a name argument."""
    if name is None:
        raise click.BadParameter(
            'Please specify the base name of your input files.',
            param_hint='"-n" / "--name"')


def validate_module(ctx, param, module=None):
    """Validate that we are given a module argument."""
    if module is None:
        raise click.BadParameter(
            'Please specify the base module of your input files.',
            param_hint='"-m" / "--module"')


def print_known_hosts(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    utils.print_possible_hosts()
    ctx.exit()


def validate_hosts(ctx, param, host=None):
    if host is None:
        host = utils.guess_host()
        if host is None:
            raise click.BadParameter(
                'Could not guess host. Please provide a value explicitly.',
                param_hint='"--host"')

    known_hosts = utils.get_possible_hosts()
    if host not in known_hosts:
        utils.print_possible_hosts()
        # raise some appropriate error here
        ctx.exit()


@cli.command()
@click.option(
    '-n',
    '--name',
    help='Name of input files. All files must have the same base name.',
    callback=validate_name)
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
    multiple=True,
    callback=validate_module)
@click.option(
    '--host',
    help='Name of the job template.',
    default=None,
    callback=validate_hosts)
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
    '--list-hosts',
    help='Show available job templates.',
    is_flag=True,
    is_eager=True,
    callback=print_known_hosts,
    expose_value=False)
@click.option(
    '--skip-validation',
    help='Skip the validation of module names.',
    default=False,
    is_flag=True)
def generate(name, gpu, module, host, min_nodes, max_nodes, time,
             skip_validation):
    """Generate benchmarks simulations from the CLI."""
    # can't be made a callback due to it being two separate options
    if min_nodes > max_nodes:
        raise click.BadParameter(
            'The minimal number of nodes needs to be smaller than the maximal number.',
            param_hint='"--min-nodes"')

    # Grab the template name for the host. This should always work because
    # click does the validation for us
    tmpl = utils.retrieve_host_template(host)

    # Warn the user that NAMD support is still experimental.
    if any(['namd' in m for m in module]):
        console.warn(
            'NAMD support is experimental. '
            'All input files must be in the current directory. '
            'Parameter paths must be absolute. Only crude file checks are performed!'
            'If you use the {} option make sure you use the GPU compatible NAMD module!',
            '--gpu')

    if not skip_validation:
        module = mdengines.normalize_modules(module)
    else:
        console.warn('Not performing module name validation.')

    for m in module:
        # Here we detect the MD engine (supported: GROMACS and NAMD).
        engine = mdengines.detect_md_engine(m)

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
