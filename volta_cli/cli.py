# Interface commands

import typer
from typing import Optional

from volta_cli import __app_name__, __version__, ERRORS
from volta_cli.server import flask_server, mysql_server

app = typer.Typer()

# login -> set mysql credentials, return success
@app.command()
def login(
    hostname: str = typer.Option(
        str(mysql_server.g_hostname),
        "--hostname",
        "-h",
        prompt="MySQL hostname",
    ),
    username: str = typer.Option(
        str(mysql_server.g_username),
        "--username",
        "-u",
        prompt="MySQL username",
    ),
    password: str = typer.Option(
        ...,
        prompt="MySQL password",
        hide_input=True
    ),
) -> None:
    # Try connecting to sql and set credentials
    # FIX DEFAULT PARAMETERS

    set_creds_error = mysql_server.set_credentials(
        hostname=hostname,
        username=username,
        password=password,
    )
    if set_creds_error:
        typer.secho(
            f'MySQL login failed with error "{ERRORS[set_creds_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    return

# start -> initialize flask server, connect to given mysql database


# build -> create/update endpoints on flask server via http request


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show application version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return