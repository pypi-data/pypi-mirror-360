import subprocess

import click
from haplohub import CreateModelRequest, PushModelRequest

from haplohub_cli.core.api.client import client

from . import run


@click.group()
def model():
    """
    Manage models
    """
    pass


@model.command()
def list():
    """
    List all models.
    """
    return client.model.list_models()


@model.command()
def build():
    """
    Build a model.
    """
    subprocess.run(["cog", "build"])


@model.command()
@click.argument("name")
def push(name, tag: str = None):
    models = client.model.list_models(name=name)
    if models.total_count == 0:
        model = client.model.create_model(CreateModelRequest(name=name))
    else:
        model = models.items[0]

    response = client.model.push_model(model.id, PushModelRequest(version="latest"))
    push_request = response.result

    subprocess.run(
        ["docker", "login", "-u", "oauth2accesstoken", "--password-stdin", f"https://{push_request.registry_host}"],
        input=push_request.push_token.encode(),
        check=True,
    )
    subprocess.run(["cog", "push", f"{push_request.registry_host}/{push_request.image_path}"], check=True)

    # TODO: Push request contains repository URL and temporary credentials.
    # TODO: Authenticate to the customer's repository using temporary credentials.
    # TODO: Use `cog push {repostiroty_url}/{name}` to push the model to the customer's repository.
    # docker login -u oauth2accesstoken --password {push_request.push_token} {push_request.repository_url}
    # cog push {push_request.repository_url}/{name}
    pass


model.add_command(run.run)
