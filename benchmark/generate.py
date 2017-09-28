from shutil import copyfile

import click
import datreant.core as dtr
import mdsynthesis as mds

from .cli import cli
from .util import ENV, normalize_host


def write_bench(top, tmpl, n, gpu, version, name, host, maxh):
    sim = mds.Sim(
        top['{}/'.format(n)],
        categories={
            'version': version,
            'gpu': gpu,
            'nodes': n,
            'host': host,
            'name': name
        })
    sim.universedef.topology = name + '.tpr'
    sim.universedef.trajectory = name + '.xtc'
    # copy input files
    mdp = '{}.mdp'.format(name)
    tpr = '{}.tpr'.format(name)
    copyfile(tpr, sim[tpr].relpath)
    copyfile(mdp, sim[mdp].relpath)
    # create bench job script
    script = tmpl.render(
        name=name, gpu=gpu, version=version, n_nodes=n, maxh=maxh)
    with open(sim['bench.job'].relpath, 'w') as fh:
        fh.write(script)


@cli.command()
@click.option('--name', help='name of tpr/mdp file')
@click.option('--gpu', is_flag=True, help='run on gpu as well')
@click.option('--version', help='gromacs module to use', multiple=True)
@click.option('--host', help='job template name', default=None)
@click.option('--max_nodes', help='test up to n nodes', type=int)
@click.option(
    '--maxh', help='runtime of tests in hours', type=float, default=.1)
def generate(name, gpu, version, host, max_nodes, maxh):
    host = normalize_host(host)
    tmpl = ENV.get_template(host)

    for v in version:
        top_folder = '{}_{}'.format(host, v)
        if gpu:
            top_folder += '_gpu'
        top = dtr.Tree(top_folder)

        for n in range(max_nodes):
            write_bench(top, tmpl, n + 1, gpu, v, name, host, maxh)
