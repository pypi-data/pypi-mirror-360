from haplohub import (
    PaginatedResponseAccessionSchema,
)
from rich.table import Table

from haplohub_cli.formatters.decorators import register


@register(PaginatedResponseAccessionSchema)
def format_metadata_accession(data: PaginatedResponseAccessionSchema):
    table = Table(title="Accession", caption=f"Total: {data.total_count}")
    # chromosome: str
    # accession: str
    # length: int
    # build: str
    # build_version: str

    table.add_column("Chromosome")
    table.add_column("Accession")
    table.add_column("Length")
    table.add_column("Build")
    table.add_column("Build Version")

    for item in data.items:
        table.add_row(
            item.chromosome,
            item.accession,
            str(item.length),
            item.build,
            item.build_version,
        )

    return table
