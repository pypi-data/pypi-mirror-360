import click
from haplohub import CreateMemberRequest, UpdateMemberRequest

from haplohub_cli.core.api.client import client

from . import report


@click.group()
def member():
    """
    Manage members
    """
    pass


@member.command()
@click.option("--cohort", "-c", type=click.STRING, required=True)
def list(cohort: str):
    return client.member.list_members(cohort)


@member.command()
@click.option("--cohort", "-c", type=click.STRING, required=True)
@click.option("--patient-id", "-p", type=str, required=False)
@click.option("--first-name", "-fn", type=str, required=False)
@click.option("--last-name", "-ln", type=str, required=False)
@click.option("--gender", "-g", type=str, required=False)
@click.option("--birth-date", "-bd", type=str, required=False)
def create(cohort, patient_id=None, first_name=None, last_name=None, gender=None, birth_date=None):
    request = CreateMemberRequest(
        patient_id=patient_id,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        birth_date=birth_date,
    )
    return client.member.create_member(cohort, request)


@member.command()
@click.argument("id")
@click.option("--cohort", "-c", type=click.STRING, required=True)
def delete(id, cohort):
    return client.member.delete_member(cohort, id)


@member.command()
@click.argument("id")
@click.option("--cohort", "-c", type=click.STRING, required=True)
@click.option("--patient-id", "-p", type=str, required=False)
@click.option("--first-name", "-fn", type=str, required=False)
@click.option("--last-name", "-ln", type=str, required=False)
@click.option("--gender", "-g", type=str, required=False)
@click.option("--birth-date", "-bd", type=str, required=False)
def update(id, cohort, patient_id=None, first_name=None, last_name=None, gender=None, birth_date=None):
    request = UpdateMemberRequest(
        patient_id=patient_id,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        birth_date=birth_date,
    )
    return client.member.update_member(cohort, id, request)


member.add_command(report.report)
