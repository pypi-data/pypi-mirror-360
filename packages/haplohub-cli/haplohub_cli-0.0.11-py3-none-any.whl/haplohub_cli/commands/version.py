import click

from haplohub_cli import __version__


@click.command(name="version")
def cmd():
    """
    Get the version of the HaploHub CLI
    """
    click.echo(f"HaploHub CLI version {__version__}")
