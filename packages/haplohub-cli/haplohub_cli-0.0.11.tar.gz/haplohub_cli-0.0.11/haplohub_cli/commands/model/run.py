import click

from haplohub_cli.core.api.client import client


@click.group()
def run():
    """
    Manage model runs
    """
    pass


@run.command()
@click.argument("model_id")
@click.option("--input-file", "-i", type=click.STRING, required=False)
@click.option("--input-data", "-I", type=click.STRING, required=False)
@click.option("--wait", "-w", is_flag=True)
def create(model_id, input_file: str = None, input_data: str = None, wait: bool = False):
    """
    1. Fetches model information.
    2. Ensures input data is valid.
    3. Call an API to run the model with input data.
    4. Pass wait flag to wait for the job to finish.
      4.1 Poll the job run status until it's finished.
    5. Return either the job run metadata or the job results.
    """
    pass


@run.command()
def list():
    return client.run.list_runs()


@run.command()
@click.argument("run_id")
def status(run_id):
    """
    1. Fetches job run information.
    2. Return the job run status.
    """
    pass


@run.command()
@click.argument("run_id")
def logs(run_id):
    """
    1. Fetches job run logs.
    2. Return the job run logs.
    """
    pass


@run.command()
@click.argument("run_id")
def results(run_id):
    """
    1. Fetches job run results.
    2. Return the job run results.
    """
    pass
