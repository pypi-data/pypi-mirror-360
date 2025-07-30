import click

from haplohub_cli.core.api.client import client


@click.group()
def metadata():
    """
    Manage metadata
    """
    pass


@metadata.command()
def accession():
    return client.metadata.list_accession()
