import click
from haplohub import GetVariantRequest, LookupHgvsRequest, VariantRange

from haplohub_cli.core.api.client import client
from haplohub_cli.types.variant_range import VariantRangeType


@click.group()
def variant():
    """
    Work with variants
    """
    pass


@variant.command()
@click.option("--sample_id", "-s", type=int, required=True)
@click.option("--cohort", "-c", type=str, required=True)
@click.option(
    "--ranges",
    "-r",
    type=VariantRangeType(),
    multiple=True,
    required=True,
    help="Variant ranges to fetch in format <accession>:<start>:<end>",
)
def fetch(sample_id: str, cohort: str, ranges: list[tuple[str, int, int]]):
    request = GetVariantRequest(
        sample_id=sample_id,
        variants=[
            VariantRange(
                accession=accession,
                start=start,
                end=end,
            )
            for accession, start, end in ranges
        ],
    )

    return client.variant.get_variant(cohort, request)


@variant.command()
@click.option("--sample_id", "-s", type=int, required=True)
@click.option("--cohort", "-c", type=str, required=True)
@click.option(
    "--hgvs",
    "-h",
    type=str,
    multiple=True,
    required=True,
    help="HGVS variants to lookup",
)
def lookup_hgvs(sample_id: str, cohort: str, hgvs: list[str]):
    request = LookupHgvsRequest(
        sample_id=sample_id,
        hgvs=hgvs,
    )

    return client.variant.lookup_hgvs(cohort, request)
