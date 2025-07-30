from haplohub import (
    CohortSchema,
    CreateCohortResponse,
    PaginatedResponseCohortSchema,
)
from rich.table import Table

from haplohub_cli.formatters import utils
from haplohub_cli.formatters.decorators import register


@register(CohortSchema)
def format_cohort(data: CohortSchema):
    table = Table(title="Cohort", caption=f"Id: {data.id}")
    table.add_column("Id")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Created")
    table.add_row(str(data.id), data.name, data.description, utils.format_dt(data.created))
    return table


@register(PaginatedResponseCohortSchema)
def format_cohorts(data: PaginatedResponseCohortSchema):
    table = Table(title="Cohorts", caption=f"Total: {data.total_count}")
    table.add_column("Id")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Created")

    for item in data.items:
        table.add_row(str(item.id), item.name, utils.truncate(item.description, 50), utils.format_dt(item.created))

    return table


@register(CreateCohortResponse)
def format_create_cohort(data: CreateCohortResponse):
    return format_cohort(data.result)
