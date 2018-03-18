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
from .mdengines import (SUPPORTED_ENGINES, detect_md_engine,
                        get_available_modules, validate_module_name)
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
@click.option(
    '--skip-validation',
    help='Skip the validation of module names.',
    default=False,
    is_flag=True)
def generate(name, gpu, module, host, min_nodes, max_nodes, time, list_hosts,
             skip_validation):
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

    if not module:
        raise click.BadParameter(
            'You did not specify which gromacs module to use for scaling.',
            param_hint='"-m" / "--module"')

    # Make sure we only warn the user once, if they are using NAMD.
    if any(['namd' in m for m in module]):
        console.warn(
            'NAMD support is experimental. '
            'All input files must be in the current directory. '
            'Parameter paths must be absolute. Only crude file checks are performed!'
            'If you use the {} option make sure you use the GPU compatible NAMD module!',
            '--gpu')

    ## TODO: Validation start
    # Save requested modules as a Set
    requested_modules = set(module)

    # Make sure that we stop if the user requests any unsupported engines.
    for req_module in requested_modules:
        if not detect_md_engine(req_module):
            console.error(
                "There is currently no support for '{}'. Supported MD engines are: {}.",
                req_module, ', '.join(sorted(SUPPORTED_ENGINES.keys())))

    # Grab all available modules on the host
    available_modules = get_available_modules()
    # Save all valid requested module version
    modules = [
        m for m in module
        if validate_module_name(module=m, available_modules=available_modules)
    ]
    # Create a list of the difference between requested and available modules
    missing_modules = requested_modules.difference(modules)

    # Warn the user that we are not going to perform any validation on module
    # names.
    if skip_validation or not available_modules:
        warning = 'Not performing module name validation.'
        if available_modules is None:
            warning += ' Cannot locate modules available on this host.'
        console.warn(warning)

    # Inform the user of all modules that are not available. Offer some alternatives.
    if available_modules and missing_modules and not skip_validation:
        # Define a default message.
        err = 'We have problems finding all of your requested modules on this host.\n'

        # Create a dictionary containing all requested engines and the
        # corresponding missing versions. This way we can list them all in a
        # nice way!
        d = {}
        for mm in missing_modules:
            engine, version = mm.split('/')
            if not engine in d:
                d[engine] = []
            d[engine].append(version)

        args = []
        for engine in d.keys():
            err += 'We were not able to find the following modules for MD engine {}: {}.\n'
            args.append(engine)
            args.extend(d[engine])

            # If we know the MD engine that the user was trying to use, we can
            # show all available options.
            err += ' Available modules are:\n{}'
            args.extend([
                '\n'.join([
                    '{}/{}'.format(engine, mde)
                    for mde in available_modules[engine]
                ])
            ])
        console.error(err, bold=True, *args)
    ## TODO: Validation end

    for m in module:
        # Here we detect the MD engine (supported: GROMACS and NAMD).
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
