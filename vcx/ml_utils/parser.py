# Preprocessing script user input parser for MySQL entries

from typing import List

from vcx.server import mysql_server
from vcx import (
    Login,
    SUCCESS
)

class Argument():
    def __init__(self, name: str, values: List[str]):
        self.name = name
        self.values = values

class Command():
    def __init__(self, name: str):
        self.name = name
        self.args: List[Argument] = []

def _parse_to_strs(script: str) -> List[str]:
    """ Convert string script from MySQL db to list """
    if script == " ":
        return []
    
    return script.split(" $")[1:]

def parse_to_commands(script: str) -> List[Command]:
    # edge case - empty
    output = []
    if script == " ":
        return output
    
    commands = script.split(" $")[1:]
    for c in commands:
        elements = c.split(" ")
        output.append(Command(elements[0]))
        for i in range(1, len(elements), 2):
            output[-1].args.append(Argument(
                name=elements[i][1:],
                values=elements[i+1].split(",")
            ))

    return output

def push_script(login: Login, position: int, command: str) -> int:
    """ Add command to preprocessing script """
    # CHECK FOR ILLEGAL COMMAND

    # Get string script
    script, getscript_error = mysql_server.getscript(login=login)
    if getscript_error:
        return getscript_error
    
    # Convert to commands and insert new command from user
    parsed_script = _parse_to_strs(script)
    if position == -1:
        position = len(parsed_script)
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
    script, getscript_error = mysql_server.getscript(login=login)
    if getscript_error:
        return getscript_error
    
    # Convert to commands and insert new command from user
    parsed_script = _parse_to_strs(script)
    position = len(parsed_script) - 1 if position == -1 else position
    parsed_script.pop(position)

    # Convert back to list and str format, update db
    appended_script = " $" + " $".join(parsed_script) if parsed_script else " "
    setscript_error = mysql_server.setscript(login, appended_script)
    if setscript_error:
        return setscript_error

    return SUCCESS