import click
from haplohub import CreateSampleRequest, UpdateSampleRequest

from haplohub_cli.core.api.client import client


@click.group()
def sample():
    """
    Manage samples
    """
    pass


@sample.command()
@click.option("--cohort", "-c", type=click.STRING, required=True)
def list(cohort: str):
    return client.sample.list_samples(cohort)


@sample.command()
@click.option("--cohort", "-c", type=click.STRING, required=True)
@click.option("--patient-id", "-p", type=click.STRING, required=False)
@click.option("--sample-id", "-s", type=click.STRING, required=False)
def create(cohort, sample_id=None, patient_id=None):
    request = CreateSampleRequest(
        sample_id=sample_id,
        patient_id=patient_id,
    )
    return client.sample.create_sample(cohort, request)


@sample.command()
@click.argument("id")
@click.option("--cohort", "-c", type=click.STRING, required=True)
def delete(id, cohort):
    return client.sample.delete_sample(cohort, id)


@sample.command()
@click.argument("id")
@click.option("--cohort", "-c", type=click.STRING, required=True)
@click.option("--patient-id", "-p", type=click.STRING, required=False)
@click.option("--sample-id", "-s", type=click.STRING, required=False)
def update(id, cohort, patient_id=None, sample_id=None):
    request = UpdateSampleRequest(
        patient_id=patient_id,
        sample_id=sample_id,
    )
    return client.sample.update_sample(cohort, id, request)
