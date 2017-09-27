import socket
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
            raise RuntimeError(
                "Couldn't guess host. Please provide explicit host")
    return host
