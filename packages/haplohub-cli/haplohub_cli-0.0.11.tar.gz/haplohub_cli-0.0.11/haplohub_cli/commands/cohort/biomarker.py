import click

from haplohub_cli.core.api.client import client


@click.group()
def biomarker():
    """
    Manage biomarkers
    """
    pass


@biomarker.command()
@click.option("--cohort", "-c", type=click.STRING, required=True)
@click.option("--order", "-o", type=click.STRING, required=False)
def result(cohort: str, order: str = None):
    return client.biomarker.list_biomarker_results(cohort, order)
