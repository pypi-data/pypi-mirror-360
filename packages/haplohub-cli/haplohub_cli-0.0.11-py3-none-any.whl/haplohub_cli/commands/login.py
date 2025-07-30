from typing import Optional

import click

from haplohub_cli.auth.auth import interactive_login, token_login


@click.command(name="login")
@click.option("--token", type=str, help="Token")
def cmd(token: Optional[str] = None):
    """
    Login to HaploHub
    """
    if token is None:
        interactive_login()
    else:
        token_login(token)
