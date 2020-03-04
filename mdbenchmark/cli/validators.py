import click

from mdbenchmark import console, utils


def validate_name(ctx, param, name=None):
    """Validate that we are given a name argument."""
    if name is None:
        raise click.BadParameter(
            "Please specify the base name of your input files.",
            param_hint='"-n" / "--name"',
        )

    return name


def validate_module(ctx, param, module=None):
    """Validate that we are given a module argument."""
    if module is None or not module:
        raise click.BadParameter(
            "Please specify which MD engine module to use for the benchmarks.",
            param_hint='"-m" / "--module"',
        )
    return module


def validate_cpu_gpu_flags(cpu, gpu):
    """Validate that either the CPU or GPU flag is set to True.
    """
    if not (cpu or gpu):
        raise click.BadParameter(
            "You must select either CPUs or GPUs to run the benchmarks on.",
            param_hint='"--cpu" / "--gpu"',
        )


def validate_number_of_nodes(min_nodes, max_nodes):
    """Validate that the minimal number of nodes is smaller than the maximal
    number.
    """
    if min_nodes > max_nodes:
        raise click.BadParameter(
            "The minimal number of nodes needs to be smaller than the maximal number.",
            param_hint='"--min-nodes"',
        )


def print_known_hosts(ctx, param, value):
    """Callback to print all available hosts to the user."""
    if not value or ctx.resilient_parsing:
        return
    utils.print_possible_hosts()
    ctx.exit()


def validate_hosts(ctx, param, host=None):
    """Callback to validate the hostname received as input.

    If we were not given a hostname, we first try to guess it via
    `utils.guess_host`. If this fails, we give up and throw an error.

    Otherwise we compare the provided/guessed host with the list of available
    templates. If the hostname matches the template name, we continue by
    returning the hostname.
    """
    if host is None:
        host = utils.guess_host()
        if host is None:
            raise click.BadParameter(
                "Could not guess host. Please provide a value explicitly.",
                param_hint='"--host"',
            )

    known_hosts = utils.get_possible_hosts()
    if host not in known_hosts:
        console.info("Could not find template for host '{}'.", host)
        utils.print_possible_hosts()
        # TODO: Raise some appropriate error here
        ctx.exit()
        return

    return host
