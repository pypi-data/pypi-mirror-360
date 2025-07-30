from haplohub import (
    ErrorResponse,
    ResultResponse,
)
from rich.text import Text

from haplohub_cli.formatters.decorators import register


@register(ErrorResponse)
def format_error_response(data: ErrorResponse):
    return Text(f"Error [{data.error.code}]: {data.error.message}", style="red")


@register(ResultResponse)
def format_result_response(data: ResultResponse):
    if data.status == "success":
        return Text("Result: Operation successful", style="green")
    else:
        return Text("Error: Operation failed", style="red")
