import click

from haplohub_cli.config.config_manager import config_manager
from haplohub_cli.config.environments import ENVIRONMENTS


@click.group()
def config():
    """
    Manage configuration
    """
    pass


@config.command()
def show():
    return config_manager.config


@config.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    setattr(config_manager.config, key, value)
    config_manager.save()
    return config_manager.config


@config.command()
@click.argument("environment", type=click.Choice(ENVIRONMENTS.keys()))
def switch(environment):
    config_manager.switch_environment(environment)
    return config_manager.config


@config.command()
def reset():
    config_manager.reset()
    config_manager.save()
    return config_manager.config
