import click


class VariantRangeType(click.ParamType):
    name = "variant_range"

    def convert(self, value, param, ctx):
        if not isinstance(value, str):
            self.fail(f"Invalid variant range: {value}", param, ctx)

        try:
            accession, start, end = value.split(":")
            return accession, int(start), int(end)
        except ValueError:
            self.fail(f"Invalid variant range: {value}", param, ctx)
