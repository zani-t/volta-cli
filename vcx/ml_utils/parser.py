# Preprocessing script user input parser for MySQL entries

from typing import List

from vcx.server import mysql_server
from vcx import (
    Login,
    SUCCESS
)

def _parse_to_commands(script: str) -> List[str]:
    """ Convert string script from MySQL db to list """
    if script == " ":
        return []
    
    return script.split(" $")[1:]

def push_script(login: Login, position: int, command: str) -> int:
    """ Add command to preprocessing script """
    # Get string script
    script, getscript_error = mysql_server.getscript(login)
    if getscript_error:
        return getscript_error
    
    # Convert to commands and insert new command from user
    parsed_script = _parse_to_commands(script)
    position = len(parsed_script) if -1 else position
    parsed_script.insert(position, command)

    # Convert back to list and str format, update db
    appended_script = " $" + " $".join(parsed_script)
    setscript_error = mysql_server.setscript(login, appended_script)
    if setscript_error:
        return setscript_error

    return SUCCESS

def pop_script(login: Login, position: int) -> int:
    """ Remove command from preprocessing script """
    # Get string script
    script, getscript_error = mysql_server.getscript(login)
    if getscript_error:
        return getscript_error
    
    # Convert to commands and insert new command from user
    parsed_script = _parse_to_commands(script)
    position = len(parsed_script) - 1 if position == -1 else position
    parsed_script.pop(position)

    # Convert back to list and str format, update db
    appended_script = " $" + " $".join(parsed_script) if parsed_script else " "
    setscript_error = mysql_server.setscript(login, appended_script)
    if setscript_error:
        return setscript_error

    return SUCCESS