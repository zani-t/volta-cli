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
    login, read_config_error = config.read_config()

    # Nonexistent/invalid
    if read_config_error:
        typer.secho(
            f'[Volta] Logged out with current status "{ERRORS[read_config_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    ext = ""
    if "database" in login.args:
        ext = f', project={login.args["project"]}, modelset={login.args["modelset"]}'

    # Valid
    typer.secho(
        f'[Volta] Logged in to MySQL with connection host={login.args["host"]}, user={login.args["user"]}' + ext,
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
    # Initialize login object and write to config
    login = Login(
        host=hostname,
        user=username,
        password=password,
    )
    write_config_error = config.write_config(login)
    if write_config_error:
        typer.secho(
            f'[Volta] MySQL login failed with error "{ERRORS[write_config_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Success
    typer.secho(
        f'[Volta] Logged in to MySQL with connection host={login.args["host"]}, user={login.args["user"]}',
        fg=typer.colors.GREEN,
    )

    return

@app.command()
def logout():
    """ Logout -> Destroy config file """
    # Check for error
    destroy_user_error = config.destroy_user()
    if destroy_user_error:
        typer.secho(
            f'[Volta] MySQL logout failed with error "{ERRORS[destroy_user_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(
        f'[Volta] Logged out',
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
            f'[Volta] MySQL connection failed with error "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'[Volta] Starting with MySQL connection host={login.args["host"]}, user={login.args["user"]}',
        fg=typer.colors.GREEN,
    )

    # Update & run
    start_error = flask_server.start()
    if start_error:
        typer.secho(
            f'[Volta] Flask startup failed with error "{ERRORS[start_error]}"',
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
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Create database
    init_error = mysql_server.init(login)
    if init_error:
        typer.secho(
            f'[Volta] Database initialization failed with status "{ERRORS[init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Rewrite config
    login.args.update({
        "database" : "volta",
        "project" : "Unsorted",
        "modelset" : "Unsorted",
    })
    write_config_error = config.write_config(login)
    if write_config_error:
        typer.secho(
            f'[Volta] Config rewrite failed with error "{ERRORS[write_config_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(
        f"[Volta] Successfully initialized database 'volta', tables 'projects', 'modelsets', 'datasets', 'models', and 'endpoints', project 'unsorted', and group 'unsorted'",
        fg=typer.colors.GREEN,
    )

    return

@app.command()
def destroy(
    # Confirmation prompt
    confirm: str = typer.Option(
        ...,
        prompt="Confirm you want to delete database 'volta' (forever!). Enter 'y'",
    )
) -> None:
    """ Delete database 'volta' """
    # Cancel if not confirmed
    if confirm != 'y':
        typer.secho('[Volta] Operation cancelled', fg=typer.colors.RED)
        raise typer.Exit(1)

    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Delete
    drop_error = mysql_server.destroy(login)
    if drop_error:
        typer.secho(
            f'[Volta] Database destruction failed with status "{ERRORS[drop_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Rewrite config
    login.args.pop("database")
    login.args.pop("project")
    login.args.pop("modelset")
    write_config_error = config.write_config(login)
    if write_config_error:
        typer.secho(
            f'[Volta] Config rewrite failed with error "{ERRORS[write_config_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Success
    typer.secho(f"[Volta] Destroyed database 'volta'", fg=typer.colors.BRIGHT_YELLOW)

    return

""" PROJECT LEVEL """

# create project
# ...

# delete project
# ...

# list projects
# ...

# enter project


# exit project
# ...

""" MODELSET LEVEL """

# create modelset
# ...

# delete modelset
# ...

# list modelset
# ...

# enter modelset
# ...

# exit modelset
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