import click

from .options import AliasedGroup

@click.command(cls=AliasedGroup)
@click.version_option()
def cli():
    """Generate, run and analyze benchmarks of molecular dynamics simulations."""
    pass

@cli.command()
def analyze():
    """Analyze docstring."""
    from .analyze import do_analyze

    do_analyze()
