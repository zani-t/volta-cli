import typer

import configparser

from pathlib import Path

from volta_cli import (
    Login,
    CONFIG_WRITE_ERROR, DIR_ERROR, FILE_ERROR, MYSQL_CONN_ERROR, SUCCESS,
    __app_name__,
)
from volta_cli.server import mysql_server

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

def login_status() -> int | Login:
    """ Check for existing config file with users (+ valid connection to MYSQL) """
    # Check if config file exists
    if not CONFIG_FILE_PATH.exists():
        return FILE_ERROR
    
    # Read config login and ping
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_FILE_PATH)
    login = Login(
        hostname=config_parser["Config"]["hostname"],
        username=config_parser["Config"]["username"],
        password=config_parser["Config"]["password"],
    )
    ping_error = mysql_server.ping(login)
    if ping_error:
        return MYSQL_CONN_ERROR
    
    return login

def init_user(login: Login) -> int:
    """ init_user -> Set login details in config file """
    # Check if MySQL login is valid
    ping_error = mysql_server.ping(login)
    if ping_error:
        return ping_error
    
    # Create config file and check if user exists already
    init_config_error = _init_config_file()
    if init_config_error:
        return init_config_error

    # Write to config file
    config_parser = configparser.ConfigParser()
    config_parser["Config"] = {
        "hostname" : login.hostname,
        "username" : login.username,
        "password" : login.password,
    }
    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return CONFIG_WRITE_ERROR

    return SUCCESS

def _init_config_file() -> int:
    """ _init_config_file -> Create config file if nonexistent """
    # Create directory
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return DIR_ERROR
    
    # Create file if nonexistent
    try:
        if not CONFIG_FILE_PATH.exists():
            CONFIG_FILE_PATH.touch()
    except OSError:
        return FILE_ERROR

    return SUCCESS

def destroy_user() -> int:
    """ destroy_user -> Destroy config file if exists """

    # Ensure config file exists
    if not CONFIG_FILE_PATH.exists():
        return FILE_ERROR
    
    # Remove
    CONFIG_FILE_PATH.unlink()

    return SUCCESS