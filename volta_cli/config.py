import typer

import configparser

from pathlib import Path

from volta_cli import (
    Login, LoginResponse,
    ERR_CONFIG_FILE, ERR_CONFIG_WRITE, ERR_CONFIG_DIR, ERR_MYSQL_CONN, SUCCESS,
    __app_name__,
)
from volta_cli.server import mysql_server

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

def read_config() -> LoginResponse:
    """ Check for existing config file with users (+ valid connection to MYSQL) """
    # Check if config file exists
    if not CONFIG_FILE_PATH.exists():
        return LoginResponse(None, ERR_CONFIG_FILE)
    
    # Read config login details
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_FILE_PATH)
    login = Login(
        hostname=config_parser["Login"]["host"],
        username=config_parser["Login"]["user"],
        password=config_parser["Login"]["password"]
    )
    if config_parser.has_option("Login", "database"):
        login.args.update({
            "database" : "volta",
            "project" : config_parser["Login"]["project"],
            "modelset" : config_parser["Login"]["modelset"],
        })

    # Test connection
    ping_status = mysql_server.ping(login)
    if ping_status == ERR_MYSQL_CONN:
        return LoginResponse(login, ERR_MYSQL_CONN)
    
    return LoginResponse(login, SUCCESS)

def write_config(login: Login) -> int:
    """ init_user -> Set login details in config file """
    # Check if MySQL login is valid
    ping_status = mysql_server.ping(login)
    if ping_status == ERR_MYSQL_CONN:
        return ERR_MYSQL_CONN

    if not ping_status:
        login.args.update({
            "database" : "volta",
            "project" : "Unsorted",
            "modelset" : "Unsorted",
        })
    
    # Create config file and check if user exists already
    init_config_error = _init_config_file()
    if init_config_error:
        return init_config_error

    # Write to config file
    config_parser = configparser.ConfigParser()
    
    config_parser["Login"] = login.args
    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return ERR_CONFIG_WRITE

    return SUCCESS

def _init_config_file() -> int:
    """ _init_config_file -> Create config file if nonexistent """
    # Create directory
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return ERR_CONFIG_DIR
    
    # Create file if nonexistent
    try:
        if not CONFIG_FILE_PATH.exists():
            CONFIG_FILE_PATH.touch()
    except OSError:
        return ERR_CONFIG_FILE

    return SUCCESS

def destroy_user() -> int:
    """ destroy_user -> Destroy config file if exists """
    # Ensure config file exists
    if not CONFIG_FILE_PATH.exists():
        return ERR_CONFIG_FILE
    
    # Remove
    CONFIG_FILE_PATH.unlink()

    return SUCCESS