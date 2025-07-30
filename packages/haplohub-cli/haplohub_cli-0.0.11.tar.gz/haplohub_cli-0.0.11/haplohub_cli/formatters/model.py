from haplohub import (
    MLModelSchema,
    PaginatedResponseMLModelSchema,
)
from rich.table import Table

from haplohub_cli.formatters import utils
from haplohub_cli.formatters.decorators import register


@register(MLModelSchema)
def format_model(data: MLModelSchema):
    table = Table(title="Model", caption=f"Id: {data.id}")
    table.add_column("Id")
    table.add_column("Name")
    table.add_column("Created")
    table.add_row(str(data.id), data.name, utils.format_dt(data.created))
    return table


@register(PaginatedResponseMLModelSchema)
def format_models(data: PaginatedResponseMLModelSchema):
    table = Table(title="Models", caption=f"Total: {data.total_count}")
    table.add_column("Id")
    table.add_column("Name")
    table.add_column("Created")

    for item in data.items:
        table.add_row(str(item.id), item.name, utils.format_dt(item.created))

    return table
