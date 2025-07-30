import click
from haplohub import CreateCohortRequest

from haplohub_cli.commands.cohort import biomarker, member, sample
from haplohub_cli.core.api.client import client


@click.group()
def cohort():
    """
    Manage cohorts
    """
    pass


@cohort.command()
def list():
    return client.cohort.list_cohorts()


@cohort.command()
@click.argument("name")
@click.option("--description", type=str, required=False)
def create(name, description=None):
    description = description or ""

    request = CreateCohortRequest(name=name, description=description)
    return client.cohort.create_cohort(request)


@cohort.command()
@click.argument("id")
def delete(id):
    return client.cohort.delete_cohort(id)


@cohort.command()
def accession():
    return client.metadata.list_accession()


cohort.add_command(biomarker.biomarker)
cohort.add_command(member.member)
cohort.add_command(sample.sample)
