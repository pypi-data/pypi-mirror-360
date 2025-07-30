import click

from haplohub_cli.commands import cohort, config, file, login, metadata, variant, version
from haplohub_cli.commands.model import model
from haplohub_cli.formatters.formatter_registry import formatter_registry


@click.group()
def cli():
    """
    HaploHub CLI

    To get started, take a look at the documentation:
    https://github.com/haplotypelabs/haplohub-cli
    """
    pass


@cli.result_callback()
def formatter_callback(result):
    if result is None:
        return

    if not formatter_registry.has_formatter(type(result)):
        from pprint import pprint

        pprint(result)
        return

    formatter_registry.format(result)


cli.add_command(cohort.cohort)
cli.add_command(config.config)
cli.add_command(file.file)
cli.add_command(login.cmd)
cli.add_command(metadata.metadata)
cli.add_command(version.cmd)
cli.add_command(variant.variant)
cli.add_command(model.model)

if __name__ == "__main__":
    cli()
