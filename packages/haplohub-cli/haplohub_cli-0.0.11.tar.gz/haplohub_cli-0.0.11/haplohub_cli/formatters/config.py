from rich.table import Table

from haplohub_cli.config.config import Config
from haplohub_cli.formatters.decorators import register


@register(Config)
def format_config(data: Config):
    table = Table(title="Config")
    table.add_column("Key")
    table.add_column("Value")

    for key, value in data.dict().items():
        table.add_row(key, str(value))
    return table
