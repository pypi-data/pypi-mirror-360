from haplohub import (
    FileSchema,
    ResultResponseFileDirSchema,
    ResultResponseFileSchema,
)
from rich.table import Table

from haplohub_cli.formatters import utils
from haplohub_cli.formatters.decorators import register


@register(FileSchema)
def format_file(data: FileSchema):
    table = Table(title="File", caption=f"Id: {data.id}")
    table.add_column("Id")
    table.add_column("File name")
    table.add_column("Size")
    table.add_column("Created")
    table.add_row(str(data.id), data.location, str(data.file_size), utils.format_dt(data.created))
    return table


@register(ResultResponseFileDirSchema)
def format_files(data: ResultResponseFileDirSchema):
    result = data.result
    table = Table(
        title=f"Contents of {result.location or 'ROOT'}",
        caption=f"Total files: {len(result.files)}, total dirs: {len(result.dirs)}",
    )
    table.add_column("Id")
    table.add_column("File name")
    table.add_column("Size")
    table.add_column("Created")

    for dir in result.dirs:
        table.add_row("DIR", dir.location + "/")

    for file in result.files:
        table.add_row(str(file.id), file.location, str(file.file_size), utils.format_dt(file.created))

    return table


@register(ResultResponseFileSchema)
def format_result_response_file(data: ResultResponseFileSchema):
    return format_file(data.result)
