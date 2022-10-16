import typer
from typing import Optional

from volta_cli import Login, config, ERRORS, __app_name__, __version__
from volta_cli.server import flask_server, mysql_server

app = typer.Typer()

""" CONFIGURATION COMMANDS """

@app.command()
def status() -> None:
    """ Status -> Check for user in config file """
    # Get login response
    login, login_error = config.read_config()

    # Nonexistent/invalid
    if login_error:
        typer.secho(
            f'Logged out with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    ext = ""
    if "database" in login.args:
        ext = f', project={login.args["project"]}, group={login.args["group"]}'

    # Valid
    typer.secho(
        f'Logged in to MySQL with connection host={login.args["host"]}, user={login.args["user"]}' + ext,
        fg=typer.colors.GREEN,
    )

    return

@app.command()
def login(
    hostname: str = typer.Option(
        str(Login.args["host"]),
        "--hostname",
        "-h",
        prompt="MySQL hostname",
    ),
    username: str = typer.Option(
        str(Login.args["user"]),
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
    login = Login(
        host=hostname,
        user=username,
        password=password,
    )
    init_user_error = config.write_config(login)
    if init_user_error:
        typer.secho(
            f'MySQL login failed with error "{ERRORS[init_user_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(
        f'Logged in to MySQL with connection host={login.args["host"]}, user={login.args["user"]}',
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
    # Check status
    login, login_error = config.read_config()

    # Nonexistent/invalid
    if login_error:
        typer.secho(
            f'MySQL connection failed with error "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'Running on MySQL with connection host={login.args["host"]}, user={login.args["user"]}',
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
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'Logged out with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Create database
    init_error = mysql_server.init(login)
    if (type(init_error) == int):
        typer.secho(
            f'Database initialization failed with status "{ERRORS[init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    return

@app.command()
def drop(
    # Confirmation prompt
) -> None:
    """ Delete database 'volta' """
    # Check login status

    # Delete

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