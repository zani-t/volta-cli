import typer
from typing import Optional

from vcx import Login, config, ERRORS, __app_name__, __version__
from vcx.ml_utils import display
from vcx.server import flask_server, mysql_server

app = typer.Typer()

@app.command()
def raw(
    query: str = typer.Option(..., prompt="Enter MySQL query")
) -> None:
    """ Run raw MySQL """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    output, raw_error = mysql_server.raw(login, query)
    if raw_error:
        typer.secho(
            f'[Volta] Raw MySQL query error "{ERRORS[raw_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(f'[Volta]\n{output}', fg=typer.colors.GREEN)

    return

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
        ext = f'\nproject={login.args["project"]}\nmodelset={login.args["modelset"]}'

    # Valid
    typer.secho(
        f'[Volta] Logged in to MySQL with connection:\nhost={login.args["host"]}\nuser={login.args["user"]}' + ext,
        fg=typer.colors.GREEN,
    )

    return

@app.command()
def login(
    hostname: str = typer.Option(str(Login.args["host"]), "--hostname", "-h",prompt="MySQL hostname"),
    username: str = typer.Option(str(Login.args["user"]), "--username", "-u",prompt="MySQL username"),
    password: str = typer.Option(..., prompt="MySQL password", hide_input=True),
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
        f"[Volta] Successfully initialized database 'volta'",
        fg=typer.colors.GREEN,
    )

    return

@app.command()
def destroy(
    # Confirmation prompt
    confirm: str = typer.Option(..., prompt="Confirm you want to delete database 'volta' (forever!). Enter 'y'")
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

@app.command("cproject")
def create_project(
    name: str = typer.Option(..., "--name", "-n", prompt="Project name"),
    desc: str = typer.Option(..., "--desc", "-d", prompt="Project description")
) -> None:
    """ Create new project """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Add entry to database
    createproj_error = mysql_server.createproj(login, name, desc)
    if createproj_error:
        typer.secho(
            f'[Volta] MySQL project creation failed with error "{ERRORS[createproj_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    createmset_error = mysql_server.createmset(login, name, "Unsorted", "Unsorted models")
    if createmset_error:
        typer.secho(
            f'[Volta] MySQL project creation failed with error "{ERRORS[createmset_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'[Volta] Created project name={name}',
        fg=typer.colors.GREEN,
    )

    return

@app.command("dproject")
def delete_project(
    name: str = typer.Option(..., "--name", "-n", prompt="Project name"),
    confirm: str = typer.Option(
        ...,
        prompt="Confirm you want to delete this project (forever!). Enter 'y'",
    ),
) -> None:
    """ Delete project """
    # Make sure not 'Unsorted'
    if name == "Unsorted":
        typer.secho(
            f"[Volta] Project 'Unsorted' cannot be removed.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
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
    deleteproj_error = mysql_server.deleteproj(login, name)
    if deleteproj_error:
        typer.secho(
            f'[Volta] MySQL project deletion failed with error "{ERRORS[deleteproj_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'[Volta] Deleted project name={name}',
        fg=typer.colors.GREEN,
    )

    return

@app.command("lprojects")
def list_projects() -> None:
    """ List projects """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Raw SQL query -> str
    output, query_error = mysql_server.raw(login, "SELECT * FROM projects")
    if query_error:
        typer.secho(
            f'[Volta] Raw MySQL query error "{ERRORS[query_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(f'[Volta]\n{output}', fg=typer.colors.GREEN)

    return

@app.command("enproject")
def enter_projects(
    name: str = typer.Option(..., "--name", "-n", prompt="Project name"),
) -> None:
    """ Enter project """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Set config file
    write_config_error = config.write_config(login, ping_project=True, proj_name=name)
    if write_config_error:
        typer.secho(
            f'[Volta] MySQL login failed with error "{ERRORS[write_config_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    typer.secho(
        f'[Volta] Entered project name={name}',
        fg=typer.colors.GREEN,
    )

    return

@app.command("exproject")
def exit_projects() -> None:
    """ Exit project """

    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if login.args["project"] == "Unsorted":
        typer.secho(
            f"[Volta] Already in project 'Unsorted'",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    login.args["project"] = "Unsorted"
    login.args["modelset"] = "Unsorted"

    # Set config file
    write_config_error = config.write_config(login)
    if write_config_error:
        typer.secho(
            f'[Volta] MySQL login failed with error "{ERRORS[write_config_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(
        f"[Volta] Now on project 'Unsorted'",
        fg=typer.colors.GREEN,
    )

    return

""" MODELSET LEVEL """

@app.command("cgroup")
def create_modelset(
    name: str = typer.Option(..., "--name", "-n", prompt="Group name"),
    desc: str = typer.Option(..., "--desc", "-d", prompt="Project description")
) -> None:
    """ Create modelset """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Create modelset
    createmset_error = mysql_server.createmset(login, name, desc)
    if createmset_error:
        typer.secho(
            f'[Volta] MySQL project creation failed with error "{ERRORS[createmset_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'[Volta] Created group name={name}',
        fg=typer.colors.GREEN,
    )

    return

@app.command("dgroup")
def delete_modelset(
    name: str = typer.Option(..., "--name", "-n", prompt="Group name"),
    confirm: str = typer.Option(..., prompt="Confirm you want to delete this group (forever!). Enter 'y'"),
) -> None:
    """ Delete modelsets """
    # Make sure not 'Unsorted'
    if name == "Unsorted":
        typer.secho(
            f"[Volta] Group 'Unsorted' cannot be removed.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
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
    deletemset_error = mysql_server.deletemset(login, name)
    if deletemset_error:
        typer.secho(
            f'[Volta] MySQL group deletion failed with error "{ERRORS[deletemset_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'[Volta] Deleted group name={name}',
        fg=typer.colors.GREEN,
    )

    return

@app.command("lgroups")
def list_modelsets(
    project: str = typer.Option(None, "--project", "-p"),
) -> None:
    """ List groups """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    ext = ""
    if project:
        # check if project exists
        proj_id, get_id_error = mysql_server.get_id(login, "projects", project)
        if get_id_error:
            typer.secho(
                f'[Volta] Query failed with current status "{ERRORS[get_id_error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        ext = f" WHERE project_id = {proj_id}"

    # Raw SQL query -> str
    output, query_error = mysql_server.raw(login, f"SELECT * FROM modelsets{ext}")
    if query_error:
        typer.secho(
            f'[Volta] Raw MySQL query error "{ERRORS[query_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(f'[Volta]\n{output}', fg=typer.colors.GREEN)

    return

@app.command("engroup")
def enter_modelset(
    name: str = typer.Option(..., "--name", "-n", prompt="Project name"),
) -> None:
    """ Enter group """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Set config file
    write_config_error = config.write_config(
        login,
        ping_project=True,
        proj_name=login.args["project"],
        modelset_name=name,
    )
    if write_config_error:
        typer.secho(
            f'[Volta] MySQL login failed with error "{ERRORS[write_config_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    typer.secho(
        f'[Volta] Entered group name={name}',
        fg=typer.colors.GREEN,
    )

    return

@app.command("exgroup")
def exit_modelset() -> None:
    """ Exit group """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if login.args["modelset"] == "Unsorted":
        typer.secho(
            f"[Volta] Already in group 'Unsorted'",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    login.args["modelset"] = "Unsorted"

    # Set config file
    write_config_error = config.write_config(login)
    if write_config_error:
        typer.secho(
            f'[Volta] MySQL login failed with error "{ERRORS[write_config_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(
        f"[Volta] Now on group 'Unsorted'",
        fg=typer.colors.GREEN,
    )

    return

""" DATASET LEVEL """

@app.command("cdataset")
def create_dataset(
    name: str = typer.Option(..., '-n', "--name", prompt="Dataset name"),
    desc: str = typer.Option(..., '-d', "--desc", prompt="Dataset description"), # list?
    location: str = typer.Option(..., '-l', "--location", prompt="Dataset location - enter 'local' or 'online'"),
    address: str = typer.Option(..., '-a', "--address", prompt="Dataset address")
) -> None:
    """ Create dataset """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    int_location = 0

    # Check location
    if location == 'online':
        int_location = 1
    elif location != 'local':
        typer.secho(
            f'[Volta] Dataset creation cancelled -- invalid location.',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Create dataset
    createds_error = mysql_server.createdataset(login, name, desc, int_location, address)
    if createds_error:
        typer.secho(
            f'[Volta] MySQL project creation failed with error "{ERRORS[createds_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'[Volta] Created group name={name}',
        fg=typer.colors.GREEN,
    )
    
    return

@app.command("ddataset")
def delete_dataset(
    name: str = typer.Option(..., "--name", "-n", prompt="Group name"),
    confirm: str = typer.Option(..., prompt="Confirm you want to delete this dataset entry. Enter 'y'"),
) -> None:
    """ Delete dataset """
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
    deletedset_error = mysql_server.deletedataset(login, name)
    if deletedset_error:
        typer.secho(
            f'[Volta] MySQL dataset deletion failed with error "{ERRORS[deletedset_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Valid
    typer.secho(
        f'[Volta] Deleted group name={name}',
        fg=typer.colors.GREEN,
    )

    return

@app.command("ldatasets")
def list_datasets() -> None:
    """ List all datasets """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Raw SQL query -> str
    output, query_error = mysql_server.raw(login, "SELECT * FROM datasets")
    if query_error:
        typer.secho(
            f'[Volta] Raw MySQL query error "{ERRORS[query_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(f'[Volta]\n{output}', fg=typer.colors.GREEN)
    return

@app.command("vdataset")
def view_dataset(
    name: str = typer.Option(..., "--name", "-n", prompt="Dataset name")
) -> None:
    """ View dataset """
    # Check login status
    login, login_error = config.read_config()
    if login_error:
        typer.secho(
            f'[Volta] Login failed with current status "{ERRORS[login_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # Get dataset address
    location, address, getds_error = mysql_server.getdataset(login, name)
    if getds_error:
        typer.secho(
            f'[Volta] Raw MySQL query error "{ERRORS[getds_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    columns, listcols_error = display.list_columns(location, address)
    if listcols_error:
        typer.secho(
            f'[Volta] Raw MySQL query error "{ERRORS[listcols_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(f'[Volta] COLUMNS:\n\n{columns}', fg=typer.colors.GREEN)
    
    return

""" PREPROCESSING SCRIPT LEVEL """

@app.command("cscript")
def create_dataset(
    name: str = typer.Option(..., '-n', "--name", prompt="Script name"),
    desc: str = typer.Option(..., '-d', "--desc", prompt="Script description"), # list?
    dataset: str = typer.Option(..., '-ds', "--dataset", prompt="Script dataset"),
    # script commands
) -> None:
    """ Create preprocessing script """
    
    return

@app.command("dscript")
def delete_dataset() -> None:
    """ Delete preprocessing script """
    
    return

@app.command("lscripts")
def list_datasets() -> None:
    """ List all preprocessing scripts """
    
    return

# edit script

""" MODEL LEVEL """

@app.command("cmodel")
def create_model(
    name: str = typer.Option(..., '-n', "--name", prompt="Model name"),
    desc: str = typer.Option(..., '-d', "--desc", prompt="Model description"), # list?
    dataset: str = typer.Option(..., '-ds', "--dataset", prompt="Model dataset"),
    arch: str = typer.Option(..., '-a', "--arch", prompt="Model architecture"),
    script: str = typer.Option(..., '-s', "--script", prompt="Model preprocessing script"),
    # hyperparameters - list
    # eval metrics - list
) -> None:
    """ Create model """

    return

@app.command("dmodel")
def delete_model() -> None:
    """ Delete model """
    
    return

@app.command("lmodels")
def list_models() -> None:
    """ List all models """
    
    return

@app.command()
def train(
    name: str = typer.Option(..., '-n', "--name", prompt="Model name")
) -> None:
    """ Train model """
    
    return

@app.command()
def deploy() -> None:
    """ Deploy model as server endpoint """
    
    return

@app.command()
def pull() -> None:
    """ Remove server endpoint model """
    
    return

from pathlib import Path
@app.command()
def test() -> None:
    p = Path(r'/home').glob('**/*')
    print([x for x in p if x.is_file()])
    return

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