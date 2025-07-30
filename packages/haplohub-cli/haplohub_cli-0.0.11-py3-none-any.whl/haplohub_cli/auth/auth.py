import webbrowser

import click

from haplohub_cli.auth.auth0_client import auth0_client
from haplohub_cli.auth.auth_web_server import AuthWebServer
from haplohub_cli.config.config_manager import config_manager
from haplohub_cli.core import ensure_config_dir
from haplohub_cli.core.network import check_port_available


def token_login(refresh_token: str):
    credentials = auth0_client.exchange_refresh_token(refresh_token)

    click.echo("Successfully authenticated with HaploHub.")
    auth0_client.token_storage.store_credentials(credentials)


def interactive_login():
    ensure_config_dir()

    if not check_port_available(config_manager.config.redirect_port):
        click.echo(
            f"Port {config_manager.config.redirect_port} is already in use. Please ensure it is free and try again.\n"
            f"Use `lsof -i4TCP:{config_manager.config.redirect_port} -sTCP:LISTEN -P -n` to find the process using the port."
        )
        exit(1)

    auth_request = auth0_client.init_auth_request()
    auth_url = auth_request.auth_url

    click.echo(
        f"Your browser has been opened to authenticate with HaploHub.\n\n    {auth_url[0 : auth_url.find('?')] + '...'}\n"
    )
    webbrowser.open(auth_url)

    auth_web_server = AuthWebServer(config_manager.config.redirect_port)
    auth_code = auth_web_server.handle_request()
    credentials = auth_request.exchange_code(auth_code)

    click.echo("Successfully authenticated with HaploHub.")
    auth0_client.token_storage.store_credentials(credentials)
