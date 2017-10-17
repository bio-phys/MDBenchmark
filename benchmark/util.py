import os
import socket
from glob import glob

import click
import numpy as np
from jinja2 import Environment, PackageLoader

ENV = Environment(loader=PackageLoader('benchmark', 'templates'))
OUTPUT_FILE_TYPES = ('*.err.*', '*.out.*', '*.log', '*.xtc', '*.cpt', '*.edr',
                     '*.po[1-9]*', '*.o[1-9]*', '*.out')


def get_possible_hosts():
    return ENV.list_templates()


def print_possible_hosts():
    all_hosts = get_possible_hosts()
    click.echo('Available host templates:')
    for h in all_hosts:
        click.echo('{}'.format(h))


def guess_host():
    hostname = socket.gethostname()
    known_hosts = get_possible_hosts()
    for h in known_hosts:
        if h in hostname:
            return h

    return None


def normalize_host(host):
    if host is None:
        host = guess_host()
        if host is None:
            raise click.BadParameter(
                'Could not guess host. Please provide a value explicitly.',
                param_hint='"-h" / "--host"')
    return host


def lin_func(x, m, b):
    return m * x + b


def calc_slope_intercept(x1, y1, x2, y2):
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - (x1 * slope)

    return np.hstack([slope, intercept])


def cleanup_before_restart(sim):
    files_found = []
    for t in OUTPUT_FILE_TYPES:
        files_found.extend(glob(os.path.join(sim.path.__str__(), t)))

    for f in files_found:
        os.remove(f)
