import os
from shutil import copyfile

import click
import datreant.core as dtr
import mdsynthesis as mds
from jinja2.exceptions import TemplateNotFound

from .cli import cli
from .util import ENV, normalize_host, print_possible_hosts


def write_bench(top, tmpl, nodes, gpu, version, name, host, time):
    sim = mds.Sim(
        top['{}/'.format(nodes)],
        categories={
            'version': version,
            'gpu': gpu,
            'nodes': nodes,
            'host': host,
            'time': time,
            'name': name,
            'started': False
        })
    sim.universedef.topology = name + '.tpr'
    # sim.universedef.trajectory = name + '.xtc'

    # copy input files
    mdp = '{}.mdp'.format(name)
    tpr = '{}.tpr'.format(name)

    if not os.path.exists(mdp):
        raise click.FileError(
            mdp, hint='File does not exist or is not readable.')
    if not os.path.exists(tpr):
        raise click.FileError(
            tpr, hint='File does not exist or is not readable.')

    copyfile(tpr, sim[tpr].relpath)
    copyfile(mdp, sim[mdp].relpath)

    maxh = time / 60.
    # Add some time buffer to the requested time. Otherwise the queuing system
    # kills the jobs before GROMACS can finish
    time += 5
    formatted_time = '{:02d}:{:02d}:00'.format(*divmod(time, 60))

    # create bench job script
    script = tmpl.render(
        name=name,
        gpu=gpu,
        version=version,
        n_nodes=nodes,
        time=time,
        formatted_time=formatted_time,
        maxh=maxh)

    with open(sim['bench.job'].relpath, 'w') as fh:
        fh.write(script)


@cli.command()
@click.option(
    '-n',
    '--name',
    help='name of tpr/mdp file',
    default='md',
    show_default=True)
@click.option(
    '-g', '--gpu', is_flag=True, help='run on gpu as well', show_default=True)
@click.option('-v', '--version', help='gromacs module to use', multiple=True)
@click.option('-h', '--host', help='job template name', default=None)
@click.option(
    '-m',
    '--max-nodes',
    help='test up to n nodes',
    default=5,
    show_default=True,
    type=int)
@click.option(
    '-t',
    '--time',
    help='run time for benchmark in minutes',
    default=15,
    show_default=True,
    type=click.IntRange(1, 1440))
@click.option('-l', '--list-hosts', help='show known hosts', is_flag=True)
def generate(name, gpu, version, host, max_nodes, time, list_hosts):
    if list_hosts:
        print_possible_hosts()
        return

    host = normalize_host(host)
    try:
        tmpl = ENV.get_template(host)
    except TemplateNotFound:
        raise click.BadParameter(
            'Could not find template for host \'{}\'.'.format(host),
            param_hint='"-h" / "--host"')

    if not version:
        raise click.BadParameter(
            'You did not specify which gromacs version to use for scaling.',
            param_hint='"-v" / "--version"')

    # Provide some output for the user
    number_of_benchmarks = click.style(
        '{}'.format(len(version) * max_nodes), bold=True)
    run_time_each = click.style('{} minutes'.format(time), bold=True)
    click.echo('Will create a total of {} benchmark systems, running {} each.'.
               format(number_of_benchmarks, run_time_each))

    for v in version:
        directory = '{}_{}'.format(host, v)
        gpu_string = '.'

        if gpu:
            directory += '_gpu'
            gpu_string = ' with GPUs.'
        top = dtr.Tree(directory)

        # More user output
        gromacs_version = click.style(
            'gromacs/{}'.format(v), blink=True, bold=True)
        click.echo('Creating benchmark system for {}{}'.format(
            gromacs_version, gpu_string))

        # More user output
        gromacs_version = click.style(
            'gromacs/{}'.format(v), blink=True, bold=True)
        click.echo('Creating benchmark system for {}{}'.format(
            gromacs_version, gpu_string))

        for n in range(max_nodes):
            write_bench(top, tmpl, n + 1, gpu, v, name, host, time)

    click.echo('Finished generating all benchmark systems.')
