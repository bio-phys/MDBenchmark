import socket

import click
from jinja2 import Environment, PackageLoader

ENV = Environment(loader=PackageLoader('benchmark', 'templates'))


def get_possible_hosts():
    return ENV.list_templates()


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
