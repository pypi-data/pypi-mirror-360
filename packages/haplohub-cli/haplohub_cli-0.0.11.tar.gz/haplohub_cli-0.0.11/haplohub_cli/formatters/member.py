from haplohub import (
    MemberSchema,
    PaginatedResponseMemberSchema,
    ResultResponseMemberSchema,
)
from rich.table import Table

from haplohub_cli.formatters import utils
from haplohub_cli.formatters.decorators import register


@register(MemberSchema)
def format_member(data: MemberSchema):
    table = Table(title="Member", caption=f"Id: {data.id}")
    table.add_column("Id")
    table.add_column("Patient ID")
    table.add_column("First Name")
    table.add_column("Last Name")
    table.add_column("Gender")
    table.add_column("Birth Date")
    table.add_column("Created")
    table.add_row(
        str(data.id),
        data.patient_id,
        data.first_name,
        data.last_name,
        data.gender,
        utils.format_date(data.birth_date),
        utils.format_dt(data.created),
    )
    return table


@register(PaginatedResponseMemberSchema)
def format_members(data: PaginatedResponseMemberSchema):
    table = Table(title="Members", caption=f"Total: {data.total_count}")
    table.add_column("Id")
    table.add_column("Patient ID")
    table.add_column("First Name")
    table.add_column("Last Name")
    table.add_column("Gender")
    table.add_column("Birth Date")
    table.add_column("Created")

    for item in data.items:
        table.add_row(
            str(item.id),
            item.patient_id,
            item.first_name,
            item.last_name,
            item.gender,
            utils.format_date(item.birth_date),
            utils.format_dt(item.created),
        )

    return table


@register(ResultResponseMemberSchema)
def format_create_member(data: ResultResponseMemberSchema):
    return format_member(data.result)
