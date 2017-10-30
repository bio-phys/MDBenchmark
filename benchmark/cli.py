import click


@click.group()
@click.version_option()
def cli():
    """Generate and run benchmark jobs for GROMACS simulations"""
    pass
