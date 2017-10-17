from shutil import copyfile

import click
import datreant.core as dtr
import mdsynthesis as mds

from .cli import cli
from .util import ENV, get_possible_hosts, normalize_host


def write_bench(top, tmpl, nodes, gpu, version, name, host, time):
    if time > 1440:
        raise ValueError('Cannot create batch jobs running longer than 24h.')

    sim = mds.Sim(
        top['{}/'.format(nodes)],
        categories={
            'version': version,
            'gpu': gpu,
            'nodes': nodes,
            'host': host,
            'time': time,
            'name': name
        })
    sim.universedef.topology = name + '.tpr'
    sim.universedef.trajectory = name + '.xtc'
    # copy input files
    mdp = '{}.mdp'.format(name)
    tpr = '{}.tpr'.format(name)
    copyfile(tpr, sim[tpr].relpath)
    copyfile(mdp, sim[mdp].relpath)

    formatted_time = '{:02d}:{:02d}:00'.format(*divmod(time, 60))
    maxh = time / 60.

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
@click.option('-n', '--name', help='name of tpr/mdp file')
@click.option('-g', '--gpu', is_flag=True, help='run on gpu as well')
@click.option('-v', '--version', help='gromacs module to use', multiple=True)
@click.option('-h', '--host', help='job template name', default=None)
@click.option('-m', '--max-nodes', help='test up to n nodes', type=int)
@click.option(
    '-t',
    '--time',
    help='run time for benchmark in minutes',
    type=int,
    default=15)
@click.option('-l', '--list-hosts', help='show known hosts', is_flag=True)
def generate(name, gpu, version, host, max_nodes, time, list_hosts):
    if list_hosts:
        print(get_possible_hosts())
        return

    host = normalize_host(host)
    tmpl = ENV.get_template(host)

    for v in version:
        top_folder = '{}_{}'.format(host, v)
        if gpu:
            top_folder += '_gpu'
        top = dtr.Tree(top_folder)

        for n in range(max_nodes):
            write_bench(top, tmpl, n + 1, gpu, v, name, host, time)
