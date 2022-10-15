import typer
from typing import Optional

from volta_cli import Login, config, ERRORS, __app_name__, __version__
from volta_cli.server import flask_server, mysql_server

app = typer.Typer()

""" CONFIGURATION COMMANDS """

@app.command()
def status() -> None:
    """ Status -> Check for user in config file """
    login_status = config.login_status()

    # Nonexistent/invalid
    if (type(login_status) == int):
        typer.secho(
            f'Logged out with current status "{ERRORS[login_status]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'Logged in to MySQL with connection host={login_status.hostname}, user={login_status.username}',
        fg=typer.colors.GREEN,
    )

    return

@app.command()
def login(
    hostname: str = typer.Option(
        str(Login.hostname),
        "--hostname",
        "-h",
        prompt="MySQL hostname",
    ),
    username: str = typer.Option(
        str(Login.username),
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
    """ Login -> Create config file with credentials """
    # !!! set default parameters
    login = Login(hostname, username, password)
    init_user_error = config.init_user(login)
    if init_user_error:
        typer.secho(
            f'MySQL login failed with error "{ERRORS[init_user_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(
        f'Logged in to MySQL with connection host={login.hostname}, user={login.username}',
        fg=typer.colors.GREEN,
    )

    return

@app.command()
def logout():
    """ Logout -> Destroy config file """
    destroy_user_error = config.destroy_user()
    if destroy_user_error:
        typer.secho(
            f'MySQL logout failed with error "{ERRORS[destroy_user_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(
        f'Logged out',
        fg=typer.colors.GREEN,
    )

""" FLASK SERVER COMMANDS """

@app.command()
def start() -> None:
    """ start -> Check login status, update & run server """
    # Check status [Repetitive]
    login_status = config.login_status()

    # Nonexistent/invalid
    if (type(login_status) == int):
        typer.secho(
            f'MySQL connection failed with error "{ERRORS[login_status]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'Running on MySQL with connection host={login_status.hostname}, user={login_status.username}',
        fg=typer.colors.GREEN,
    )

    # Update & run
    start_error = flask_server.start()
    if start_error:
        typer.secho(
            f'Flask startup failed with error "{ERRORS[start_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    return

# update -> create/update endpoints on flask server via http request
# ...

""" MYSQL COMMANDS """

""" DATABASE LEVEL """

@app.command()
def init() -> None:
    """ Initialize Volta CLI top-level database """
    # Check login status
    login_status = config.login_status()
    if (type(login_status) == int):
        typer.secho(
            f'Logged out with current status "{ERRORS[login_status]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Create database
    init_error = mysql_server.init(login_status)
    if (type(init_error) == int):
        typer.secho(
            f'Database initialization failed with status "{ERRORS[init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    return

""" PROJECT LEVEL """

# create project
# ...

# delete project
# ...

# list projects
# ...

# enter project
# ...

# exit project
# ...

""" GROUP LEVEL """

# create group
# ...

# delete group
# ...

# list groups
# ...

# [enter group]
# ...

# [exit group]
# ...

""" DATASET LEVEL """

# create dataset
# ...

# delete dataset
# ...

""" MODEL LEVEL """

# create model
# ...

# delete model
# ...

# list models
# ...

# train model
# ...

# deploy model
# ...

# pull model
# ...

""" CLI LEVEL """

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