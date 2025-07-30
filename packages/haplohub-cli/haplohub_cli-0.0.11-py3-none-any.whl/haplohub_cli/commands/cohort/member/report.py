import click

from haplohub_cli.core.api.client import client


@click.group()
def report():
    """
    Manage reports
    """
    pass


@report.command()
@click.option("--cohort", "-c", type=click.STRING, required=True)
@click.option("--member", "-m", type=click.STRING, required=True)
@click.option("--report-template", "-t", type=click.STRING, required=True)
@click.option("--output", "-o", type=click.STRING, required=True)
def create(cohort: str, member: str, report_template: str, output: str):
    response = client.member_report.create_member_report(
        cohort_id=cohort,
        member_id=member,
        report_template_id=report_template,
    )

    with open(output, "wb") as f:
        f.write(response)

    click.echo(f"Report saved to {output}")
