from shutil import copyfile

import click
import datreant.core as dtr
import mdsynthesis as mds

from .cli import cli
from .util import ENV, normalize_host


def write_bench(top, tmpl, n, gpu, version, name, host):
    sim = mds.Sim(
        top['{}/'.format(n)],
        categories={'version': version,
                    'gpu': gpu,
                    'nodes': n,
                    'host': host,
                    'name': name})
    # copy input files
    mdp = '{}.mdp'.format(name)
    tpr = '{}.tpr'.format(name)
    copyfile(tpr, sim[tpr].relpath)
    copyfile(mdp, sim[mdp].relpath)
    # create bench job script
    script = tmpl.render(name=name, gpu=gpu, version=version, n_nodes=n)
    with open(sim['bench.job'].relpath, 'w') as fh:
        fh.write(script)


@cli.command()
@click.option('--name', help='name of tpr/mdp file')
@click.option('--gpu', is_flag=True, help='run on gpu as well')
@click.option('--version', help='gromacs module to use', multiple=True)
@click.option('--host', help='job template name', default=None)
@click.option('--max_nodes', help='test up to n nodes', type=int)
def generate(name, gpu, version,  host, max_nodes):
    host = normalize_host(host)
    tmpl = ENV.get_template(host)

    for v in version:
        top_folder = v
        if gpu:
            top_folder += '-gpu'
        top = dtr.Tree(top_folder)

        for n in range(max_nodes):
            write_bench(top, tmpl, n + 1, gpu, v, name, host)
