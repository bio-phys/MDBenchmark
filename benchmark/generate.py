from shutil import copyfile

import click
import datreant.core as dtr
from jinja2 import Environment, FileSystemLoader
import mdsynthesis as mds

from .cli import cli

ENV = Environment(loader=FileSystemLoader('.'))


def write_bench(top, tmpl, n, gpu, version, name):
    sim = mds.Sim(
        top['{}/'.format(n)],
        categories={'version': version,
                    'gpu': gpu,
                    'nodes': n})
    # # copy input files
    # mdp = '{}.mdp'.format(name)
    # tpr = '{}.tpr'.format(name)
    # copyfile(tpr, sim[tpr].relpath)
    # copyfile(mdp, sim[mdp].relpath)
    # # create bench job script
    # script = tmpl.render(
    #     name=name, gpu=gpu, version=version, n_nodes=n)
    # with open(sim['bench.slurm'].relpath, 'w') as fh:
    #     fh.write(script)


@cli.command()
@click.option('--name', help='name of tpr/mdp file')
@click.option('--gpu', is_flag=True, help='run on gpu as well')
@click.option('--version', help='gromacs module to use')
@click.option('--top_folder')
@click.option('--template', help='job template name')
@click.option('--max_nodes', help='test up to n nodes')
def generate(name, gpu, version, top_folder, template, max_nodes):
    top = dtr.Tree(top_folder)
    # tmpl = ENV.get_template(args.template)
    tmpl = None

    for n in range(max_nodes):
        write_bench(top, tmpl, n + 1, gpu, version, name)
